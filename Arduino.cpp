#include "Arduino.h"
#include <stddef.h>
#include <ugpio.h>
#include <stdio.h>
#include <unistd.h>
#include <time.h>
#include <math.h>

void pinMode(uint8_t pin, uint8_t mode) {
	int rq = 0, rv = 0;
	//request pin. Pulse reset. release it.
	if ((rq = gpio_is_requested(pin)) < 0) {
		perror("gpio_is_requested");
	}
	// export the gpio
	if (!rq) {
		printf("> exporting gpio %d\n", (int) pin);
		if ((rv = gpio_request(pin, NULL)) < 0) {
			perror("gpio_request");
		}
	}

	if (mode == INPUT || mode == INPUT_PULLUP) {
		// set to input direction
		printf("> setting to input\n");
		if ((rv = gpio_direction_input(pin)) < 0) {
			perror("gpio_direction_input");
		}

		//no support for INPUT_PULLUP at the moment,
		//pins will be left floating..
	} else if (mode == OUTPUT) {
		if ((rv = gpio_direction_output(pin, HIGH)) < 0) {
			perror("gpio_direction_input");
		}
	}
}

void digitalWrite(uint8_t pin, uint8_t value) {
	gpio_set_value(pin, (int) value);
}

int digitalRead(uint8_t pin) {
	return gpio_get_value(pin);
}

void pinFree(uint8_t pin) {
	gpio_free(pin);
}

unsigned long millis(void) {
	return micros() / 1000UL;
}

unsigned long micros(void) {
    long            ms; // Milliseconds
    time_t          s;  // Seconds
    struct timespec spec;

    clock_gettime(CLOCK_REALTIME, &spec);

    s  = spec.tv_sec;
    ms = round(spec.tv_nsec / 1.0e6); // Convert nanoseconds to milliseconds
    if (ms > 999) {
        s++;
        ms = 0;
    }

    return (s * 1000UL) + ms;
}

void delay(unsigned long millis) {
	usleep(millis * 1000UL);
}

void delayMicroseconds(unsigned int us) {
	usleep(us);
}

