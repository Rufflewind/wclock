#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <wclock.h>
#ifdef _WIN32
# include <windows.h>
static unsigned int sleep(unsigned int x) { Sleep(x * 1000); return 0; }
#else
# include <unistd.h>
#endif

int main(void)
{
    double res, t1, t2;
    wclock clock;

    int e = init_wclock(&clock);
    assert(e == 0);

    res = get_wclock_res(&clock);
    printf("%.17g\n", res);
    /* presumably the clock has at least millisecond precision! */
    assert(res < 2e-3);

    t1 = get_wclock(&clock);
    printf("%.17g\n", t1);

    sleep(1);

    t2 = get_wclock(&clock);
    printf("%.17g\n", t2);
    assert(fabs(t2 - t1 - 1.) < 1e-1);

    return 0;
}
