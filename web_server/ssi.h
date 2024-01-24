#include "lwip/apps/httpd.h"
#include "pico/cyw43_arch.h"
#include "hardware/adc.h"
#include "fast.h"

// SSI tags - tag length limited to 8 bytes by default
const char * ssi_tags[] = {"status","temp"};

u16_t ssi_handler(int iIndex, char *pcInsert, int iInsertLen) {
  size_t printed;
  switch (iIndex) {
  case 0: // temp
    {
      if(status == true)
        printed = snprintf(pcInsert, iInsertLen, "Heater ON");
      else
        printed = snprintf(pcInsert, iInsertLen, "Heater OFF");
    }
    break;
  case 1: // status
    {
    printed = snprintf(pcInsert, iInsertLen, "%d", act_temp);
    }
    break;
  default:
    printed = 0;
    break;
  }

  return (u16_t)printed;
}

void ssi_init() {
  

  http_set_ssi_handler(ssi_handler, ssi_tags, LWIP_ARRAYSIZE(ssi_tags));
}
