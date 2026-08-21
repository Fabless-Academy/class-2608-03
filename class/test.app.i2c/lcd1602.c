#include    <i2c.h>
#include    <lcd.h>
#include    "lcd1602.h"


void LCD1602_Run(void)
{
    static const char *messages[][2] = {
        {"Hello World!", "LCD1602 ready."},
        {"I2C connection", "is working."},
        {"First line text", "Second line text"},
        {"Next message", "Please wait."}
    };
    uint32 message_index = 0;

    SAL_OsInitFuncs();

    // Initialize I2C and GPIO for LCD1602
    I2C_Init();
    if(I2C_Open(I2C_CH, I2C_PORT, I2C_SPEED, NULL, NULL) != SAL_RET_SUCCESS)
    {
        mcu_printf("Failed to open I2C channel\n");
        return;
    }
    uint32 detected_address = I2C_ScanSlave(I2C_CH);
    mcu_printf("Detected I2C device address: 0x%02X\n", detected_address);

    lcd_init();

    while (1)
    {
        lcd_cmd(0x01);
        SAL_TaskSleep(5);
        lcd_cmd(0x80);
        lcd_print(messages[message_index][0]);
        lcd_cmd(0xC0);
        lcd_print(messages[message_index][1]);

        SAL_TaskSleep(2000);
        message_index++;
        if (message_index >= (sizeof(messages) / sizeof(messages[0])))
        {
            message_index = 0;
        }
    }
}