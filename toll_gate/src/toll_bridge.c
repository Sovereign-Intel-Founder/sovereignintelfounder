#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <sqlite3.h>
#include <time.h>

#define PORT 8080
#define MAX_CONNECTIONS 1024
#define FREE_THRESHOLD 8

typedef struct {
    sqlite3 *db;
    unsigned long request_count;
} GatewayState;

void init_database(sqlite3 **db) {
    int rc = sqlite3_open("sip_ledger.db", db);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "Cannot open database: %s\n", sqlite3_errmsg(*db));
        exit(1);
    }

    const char *sql = 
        "PRAGMA journal_mode = WAL;"
        "PRAGMA synchronous = NORMAL;"
        "CREATE TABLE IF NOT EXISTS requests ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "client_hex TEXT NOT NULL,"
        "decision TEXT NOT NULL,"
        "timestamp DATETIME DEFAULT CURRENT_TIMESTAMP"
        ");";

    char *err_msg = 0;
    rc = sqlite3_exec(*db, sql, 0, 0, &err_msg);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "SQL error: %s\n", err_msg);
        sqlite3_free(err_msg);
        sqlite3_close(*db);
        exit(1);
    }
}

void log_request(sqlite3 *db, const char *client_hex, const char *decision) {
    char sql[256];
    snprintf(sql, sizeof(sql), "INSERT INTO requests (client_hex, decision) VALUES ('%s', '%s');", client_hex, decision);
    char *err_msg = 0;
    sqlite3_exec(db, sql, 0, 0, &err_msg);
    sqlite3_free(err_msg);
}

int main() {
    int server_fd, new_socket;
    struct sockaddr_in address;
    int opt = 1;
    int addrlen = sizeof(address);
    sqlite3 *db;

    init_database(&db);
    printf("Sovereign Intelligence Protocol C-native toll bridge active on port %d [WAL Mode Active]\n", PORT);

    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt))) {
        perror("setsockopt");
        exit(EXIT_FAILURE);
    }

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }

    if (listen(server_fd, MAX_CONNECTIONS) < 0) {
        perror("listen");
        exit(EXIT_FAILURE);
    }

    unsigned long request_counter = 0;

    while (1) {
        if ((new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen)) < 0) {
            perror("accept");
            continue;
        }

        request_counter++;
        const char *client_hex = "0101010101010101010101010101010101010101010101010101010101010101";
        
        char response[512];
        if (request_counter <= FREE_THRESHOLD) {
            log_request(db, client_hex, "ALLOW_FREE");
            snprintf(response, sizeof(response), 
                "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{\"status\": \"allowed_free\", \"tier\": \"mesh_commons\", \"count\": %lu}\r\n", 
                request_counter);
        } else {
            log_request(db, client_hex, "TRIGGER_402");
            snprintf(response, sizeof(response), 
                "HTTP/1.1 402 Payment Required\r\nContent-Type: application/json\r\n\r\n{\"error\": \"payment_required\", \"amount_sats\": 1000}\r\n");
        }

        write(new_socket, response, strlen(response));
        close(new_socket);
    }

    sqlite3_close(db);
    return 0;
}
