#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/epoll.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <fcntl.h>
#include <errno.h>
#include <sqlite3.h>
#include <pthread.h>
#include <time.h>
#include <stdatomic.h>

#define PORT 8080
#define MAX_EVENTS 8192
#define BUFFER_SIZE 2048
#define DB_PATH "/home/joshua445/sovereign_workspace/toll_bridge.db"

// Lock-Free Ring Buffer Size (Must be power of 2)
#define RING_SIZE 262144
#define RING_MASK (RING_SIZE - 1)

typedef struct {
    char client_id[64];
    int status;
    double latency_ms;
} TelemetryItem;

typedef struct {
    TelemetryItem buffer[RING_SIZE];
    _Atomic size_t head;
    _Atomic size_t tail;
} LockFreeRingBuffer;

static LockFreeRingBuffer ring = { .head = 0, .tail = 0 };

inline static int ring_push(const char* client_id, int status, double latency_ms) {
    size_t current_head = atomic_load_explicit(&ring.head, memory_order_relaxed);
    size_t current_tail = atomic_load_explicit(&ring.tail, memory_order_acquire);

    if ((current_head - current_tail) >= RING_SIZE) {
        return -1; // Ring buffer full backpressure protection
    }

    size_t index = current_head & RING_MASK;
    strncpy(ring.buffer[index].client_id, client_id, 63);
    ring.buffer[index].client_id[63] = '\0';
    ring.buffer[index].status = status;
    ring.buffer[index].latency_ms = latency_ms;

    atomic_store_explicit(&ring.head, current_head + 1, memory_order_release);
    return 0;
}

void* db_worker(void* arg) {
    sqlite3 *db;
    if (sqlite3_open(DB_PATH, &db) != SQLITE_OK) {
        fprintf(stderr, "[ERROR] DB Open failed: %s\n", sqlite3_errmsg(db));
        return NULL;
    }
    
    sqlite3_exec(db, "PRAGMA journal_mode=WAL;", 0, 0, 0);
    sqlite3_exec(db, "PRAGMA synchronous=OFF;", 0, 0, 0);
    sqlite3_exec(db, "PRAGMA locking_mode=EXCLUSIVE;", 0, 0, 0);
    sqlite3_exec(db, "CREATE TABLE IF NOT EXISTS telemetry (id INTEGER PRIMARY KEY AUTOINCREMENT, client_id TEXT, status INTEGER, latency_ms REAL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);", 0, 0, 0);

    sqlite3_stmt *stmt;
    const char *sql = "INSERT INTO telemetry (client_id, status, latency_ms) VALUES (?, ?, ?);";
    sqlite3_prepare_v2(db, sql, -1, &stmt, 0);

    while (1) {
        size_t current_tail = atomic_load_explicit(&ring.tail, memory_order_relaxed);
        size_t current_head = atomic_load_explicit(&ring.head, memory_order_acquire);

        if (current_tail == current_head) {
            struct timespec req = { .tv_sec = 0, .tv_nsec = 50000 }; // 50 microsecond pause
            nanosleep(&req, NULL);
            continue;
        }

        sqlite3_exec(db, "BEGIN TRANSACTION;", 0, 0, 0);
        while (current_tail != current_head) {
            size_t index = current_tail & RING_MASK;
            TelemetryItem *item = &ring.buffer[index];

            sqlite3_bind_text(stmt, 1, item->client_id, -1, SQLITE_STATIC);
            sqlite3_bind_int(stmt, 2, item->status);
            sqlite3_bind_double(stmt, 3, item->latency_ms);
            sqlite3_step(stmt);
            sqlite3_reset(stmt);

            current_tail++;
        }
        sqlite3_exec(db, "COMMIT;", 0, 0, 0);
        atomic_store_explicit(&ring.tail, current_tail, memory_order_release);
    }

    sqlite3_finalize(stmt);
    sqlite3_close(db);
    return NULL;
}

int set_nonblocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    return (flags == -1) ? -1 : fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}

int main() {
    pthread_t db_tid;
    pthread_create(&db_tid, NULL, db_worker, NULL);

    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("socket creation failed");
        exit(EXIT_FAILURE);
    }

    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEPORT, &opt, sizeof(opt));
    setsockopt(server_fd, IPPROTO_TCP, TCP_NODELAY, &opt, sizeof(opt));

    struct sockaddr_in address = {0};
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr*)&address, sizeof(address)) < 0) {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }

    if (listen(server_fd, 65535) < 0) {
        perror("listen failed");
        exit(EXIT_FAILURE);
    }

    set_nonblocking(server_fd);

    int epoll_fd = epoll_create1(0);
    struct epoll_event ev = {.events = EPOLLIN | EPOLLET, .data.fd = server_fd};
    epoll_ctl(epoll_fd, EPOLL_CTL_ADD, server_fd, &ev);

    struct epoll_event events[MAX_EVENTS];
    const char *http_200 = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 2\r\nConnection: keep-alive\r\n\r\nOK";
    int http_200_len = strlen(http_200);

    printf("SIP Production Bare-Metal C Toll Bridge listening on port %d\n", PORT);

    while (1) {
        int nfds = epoll_wait(epoll_fd, events, MAX_EVENTS, -1);
        for (int n = 0; n < nfds; ++n) {
            if (events[n].data.fd == server_fd) {
                while (1) {
                    struct sockaddr_in client_addr;
                    socklen_t client_len = sizeof(client_addr);
                    int client_fd = accept(server_fd, (struct sockaddr*)&client_addr, &client_len);
                    if (client_fd < 0) break;

                    setsockopt(client_fd, IPPROTO_TCP, TCP_NODELAY, &opt, sizeof(opt));
                    setsockopt(client_fd, IPPROTO_TCP, TCP_QUICKACK, &opt, sizeof(opt));
                    set_nonblocking(client_fd);

                    struct epoll_event client_ev = {.events = EPOLLIN | EPOLLET | EPOLLRDHUP, .data.fd = client_fd};
                    epoll_ctl(epoll_fd, EPOLL_CTL_ADD, client_fd, &client_ev);
                }
            } else {
                int client_fd = events[n].data.fd;
                if (events[n].events & (EPOLLRDHUP | EPOLLHUP | EPOLLERR)) {
                    epoll_ctl(epoll_fd, EPOLL_CTL_DEL, client_fd, NULL);
                    close(client_fd);
                    continue;
                }

                char buffer[BUFFER_SIZE];
                struct timespec t0, t1;
                clock_gettime(CLOCK_MONOTONIC_RAW, &t0);

                ssize_t bytes_read = read(client_fd, buffer, sizeof(buffer) - 1);
                if (bytes_read > 0) {
                    buffer[bytes_read] = '\0';
                    char client_id[64] = "bench_worker";
                    char *hdr = strstr(buffer, "X-Client-ID:");
                    if (!hdr) hdr = strstr(buffer, "x-client-id:");
                    if (hdr) sscanf(hdr + 12, "%63s", client_id);

                    clock_gettime(CLOCK_MONOTONIC_RAW, &t1);
                    double latency_ms = (t1.tv_sec - t0.tv_sec) * 1000.0 + (t1.tv_nsec - t0.tv_nsec) / 1000000.0;

                    write(client_fd, http_200, http_200_len);
                    ring_push(client_id, 200, latency_ms);
                } else if (bytes_read == 0 || (bytes_read < 0 && errno != EAGAIN)) {
                    epoll_ctl(epoll_fd, EPOLL_CTL_DEL, client_fd, NULL);
                    close(client_fd);
                }
            }
        }
    }
    close(server_fd);
    return 0;
}
