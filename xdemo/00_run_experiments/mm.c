#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <time.h>

float mm(long M, long N, long K,
         float A[M][K],
         float B[K][N],
         float C[M][N]) {
  for (long i = 0; i < M; i++) {
    for (long j = 0; j < N; j++) {
      for (long k = 0; k < K; k++) {
        C[i][j] += A[i][k] * B[k][j];
      }
    }
  }
}

long init_mat(long M, long N, float A[M][N], float c) {
  for (long i = 0; i < M; i++) {
    for (long j = 0; j < N; j++) {
      A[i][j] = c;
    }
  }
}

float * mk_matrix(long M, long N, float c) {
  float * A_ = (float *)malloc(sizeof(float) * M * N);
  float (*A)[N] = (float (*)[N])A_;
  init_mat(M, N, A, c);
  return A_;
}

int check_mm(long M, long N, long K,
             float A[M][K],
             float B[K][N],
             float C[M][N], unsigned short rg[3], long n_checks) {
  for (long t = 0; t < n_checks; t++) {
    long i = nrand48(rg) % M;
    long j = nrand48(rg) % N;
    float s = 0.0;
    for (long k = 0; k < K; k++) {
      s += A[i][k] * B[k][j];
    }
    assert(C[i][j] == s);
  }
  return 1;
}

long cur_time_ns() {
  struct timespec ts[1];
  clock_gettime(CLOCK_REALTIME, ts);
  return ts->tv_sec * 1000000000L + ts->tv_nsec;
}

long run_mm(long M, long N, long K,
            float A[M][K],
            float B[K][N],
            float C[M][N], unsigned short rg[3]) {
  init_mat(M, N, C, 0.0);
  long t0 = cur_time_ns();
  mm(M, N, K, A, B, C);
  long t1 = cur_time_ns();
  check_mm(M, N, K, A, B, C, rg, 100);
  return t1 - t0;
}

int main(int argc, char ** argv) {
  long M = atol(argv[1]);
  long N = atol(argv[2]);
  long K = atol(argv[3]);
  long seed = 111111111111111111L;
  printf("M = %ld, N = %ld, K = %ld\n", M, N, K);
  float * A_ = mk_matrix(M, K, 1.0);
  float * B_ = mk_matrix(K, N, 1.0);
  float * C_ = mk_matrix(M, N, 0.0);
  float (*A)[K] = (float (*)[K])A_;
  float (*B)[N] = (float (*)[N])B_;
  float (*C)[N] = (float (*)[N])C_;
  unsigned short rg[3] = { (seed >> 32) & 0xFFFF,
                           (seed >> 16) & 0xFFFF,
                           (seed >>  0) & 0xFFFF };
  for (long r = 0; r < 10; r++) {
    long dt = run_mm(M, N, K, A, B, C, rg);
    printf("%ld : T = %ld\n", r, dt);
  }
}
