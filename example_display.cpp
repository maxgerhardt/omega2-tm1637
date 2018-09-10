#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "TM1637.h"

int main() {

	printf("Beginning test program\n");

	uint8_t pinClk = 18;
	uint8_t pinData = 19;

	TM1637Display display(pinClk, pinData);

	display.showNumberDec(123);

	sleep(10);

	printf("Goodbye\n");

	return 0;
}
