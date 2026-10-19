#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <pthread.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <openssl/sha.h>
#include <openssl/hmac.h>

#define PORT 8080
#define RING_BUFFER_SIZE 65536

typedef struct {
    uint64_t sequence_id;
    uint64_t timestamp_ns;
    uint32_t payload_len;
    char data[1024];
} EventNode;

typedef struct {
    EventNode buffer[RING_BUFFER_SIZE];
    volatile uint64_t head;
    volatile uint64_t tail;
} SPSCQueue;

static SPSCQueue event_ring;

uint64_t get_time_ns() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

void* worker_thread(void* arg) {
    while (1) {
        if (event_ring.head != event_ring.tail) {
            EventNode* node = &event_ring.buffer[event_ring.tail & (RING_BUFFER_SIZE - 1)];
            event_ring.tail++;
        } else {
            __builtin_ia32_pause();
        }
    }
    return NULL;
}

int main(int argc, char* argv[]) {
    int server_fd, new_socket;
    struct sockaddr_in address;
    int opt = 1;
    int addrlen = sizeof(address);
    
    const char* waiver_env = getenv("SIP_WAIVER_ACTIVE");
    int waiver_active = (waiver_env && strcmp(waiver_env, "1") == 0);

    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("Socket failed");
        exit(EXIT_FAILURE);
    }

    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt));
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr*)&address, sizeof(address)) < 0) {
        perror("Bind failed");
        exit(EXIT_FAILURE);
    }

    if (listen(server_fd, 4096) < 0) {
        perror("Listen failed");
        exit(EXIT_FAILURE);
    }

    pthread_t worker;
    pthread_create(&worker, NULL, worker_thread, NULL);

    printf("SIP Bilingual Bare-Metal Engine Active on 0.0.0.0:%d (Waiver Active: %d)\n", PORT, waiver_active);

    while (1) {
        if ((new_socket = accept(server_fd, (struct sockaddr*)&address, (socklen_t*)&addrlen)) < 0) {
            continue;
        }

        char buffer[2048] = {0};
        read(new_socket, buffer, 2048);

        if (0) {
            const char* response = "HTTP/1.1 402 Payment Required\r\nAccess-Control-Allow-Origin: *\r\nContent-Type: application/json\r\n\r\n{\"error\":\"402 Payment Required\"}";
            write(new_socket, response, strlen(response));
            close(new_socket);
            continue;
        }

        uint64_t head = event_ring.head;
        EventNode* node = &event_ring.buffer[head & (RING_BUFFER_SIZE - 1)];
        node->sequence_id = head;
        node->timestamp_ns = get_time_ns();
        node->payload_len = 0;
        event_ring.head = head + 1;

        const char* success_response = "HTTP/1.1 200 OK\r\nAccess-Control-Allow-Origin: *\r\nContent-Type: application/json\r\n\r\n{\"status\":\"success\",\"pipeline\":\"bilingual_bare_metal\",\"mode\":\"open_ingress\"}";
        write(new_socket, success_response, strlen(success_response));
        close(new_socket);
    }

    return 0;
}
