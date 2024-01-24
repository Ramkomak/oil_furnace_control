#include "lwip/apps/httpd.h"
#include "pico/stdlib.h"
#include "pico/cyw43_arch.h"
#include "lwipopts.h"
#include "ssi.h"




#define UART_ID uart0
#define BAUD_RATE 9600

#define UART_TX_PIN 0
#define UART_RX_PIN 1

const char levels[11] = {'0','1','2','3','4','5','6','7','8','9'};

const char WIFI_SSID[] = "XXX";
const char WIFI_PASSWORD[] = "XXX";


void on_uart_rx() {
      
        while (uart_is_readable(UART_ID))
            {
                char ch = uart_getc(UART_ID);
                if(ch == '?') 
                {
                    char d = uart_getc(UART_ID);
                    
                    if (d == '0')
                        status = true;
                    if (d == '1')
                        status = false;
                    
                }
                if (ch == '!')
                {
                    char d = uart_getc(UART_ID);
                    char j = uart_getc(UART_ID);
                    for(u_int8_t swap = 0; swap < sizeof(levels);swap++)
                    {
                        if(d == levels[swap])
                            act_temp = 10*swap;
                    }
                    for(u_int8_t swap = 0; swap < sizeof(levels);swap++)
                    {
                        if(j == levels[swap])
                            act_temp += 1*swap;
                    }
                    break;
                }    
            }  
}

void enable_uart()
{
    uart_init(UART_ID, BAUD_RATE);
    gpio_set_function(UART_TX_PIN, GPIO_FUNC_UART);
    gpio_set_function(UART_RX_PIN, GPIO_FUNC_UART);
    
    int UART_IRQ = UART_ID == uart0 ? UART0_IRQ : UART1_IRQ;
    irq_set_exclusive_handler(UART_IRQ, on_uart_rx);
    irq_set_enabled(UART_IRQ, true);

    uart_set_irq_enables(UART_ID, true, false);

}

int main() {
    stdio_init_all();

    cyw43_arch_init();

    cyw43_arch_enable_sta_mode();

    while(cyw43_arch_wifi_connect_timeout_ms(WIFI_SSID, WIFI_PASSWORD, CYW43_AUTH_WPA2_AES_PSK, 30000) != 0){
        printf("Attempting to connect...\n");
    }
   
    httpd_init();
    

    ssi_init(); 
    
    enable_uart();
    
    while(1);
}