#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>
#include <errno.h>

#define DEFAULT_SHM_NAME "/sovereign_live_ring"
#define MAX_RETRIES 15
#define RETRY_DELAY_US 500000 // 500ms retry backoff

int main() {
    // Read segment name from environment variable with a safe fallback
    const char *shm_name = getenv("SOVEREIGN_SHM_NAME");
    if (!shm_name) {
        shm_name = DEFAULT_SHM_NAME;
    }

    int fd = -1;
    int retries = 0;

    printf("[LATENCY-WORKER] Initializing data-plane listener. Target SHM: %s\n", shm_name);

    // Resilient startup loop: wait for the producer to materialize the ring buffer
    while (retries < MAX_RETRIES) {
        fd = shm_open(shm_name, O_RDWR, 0666);
        if (fd != -1) {
            break;
        }
        if (errno == ENOENT) {
            printf("[LATENCY-WORKER] Segment %s not found yet. Retrying (%d/%d)...\n", 
                   shm_name, retries + 1, MAX_RETRIES);
            usleep(RETRY_DELAY_US);
        } else {
            perror("[LATENCY-WORKER] Critical shm_open failure");
            break;
        }
        retries++;
    }

    if (fd == -1) {
        fprintf(stderr, "[LATENCY-WORKER] Failed to attach to shared memory after %d retries. Aborting.\n", MAX_RETRIES);
        exit(1);
    }

    printf("[LATENCY-WORKER] Successfully attached to live ring buffer descriptor: %d\n", fd);

    // Active polling / telemetry consumption loop
    while (1) {
        // Real-time zero-copy ring buffer processing goes here
        usleep(1000000);
    }

    close(fd);
    return 0;
}
