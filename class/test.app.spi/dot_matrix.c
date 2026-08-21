#include "dot.matrix.h"
#include <stdint.h>
#include <gpio.h>
#include <gpsb.h>


void max7219_send(uint8_t addr, uint8_t data)
{
    uint8_t tx[2] = { addr, data }, rx[2] = {0};
    GPSB_CsActivate (MAX7219_CHANNEL, MAX7219_CS_GPIO, FALSE);
    GPSB_Xfer       (MAX7219_CHANNEL, tx, rx, 2, GPSB_XFER_MODE_WITHOUT_INTERRUPT);
    GPSB_CsDeactivate(MAX7219_CHANNEL, MAX7219_CS_GPIO, FALSE); 
}

void max7219_init(void) // FUNC 설정
{
    GPIO_Config(MAX7219_CS_GPIO,   GPIO_FUNC(0) | GPIO_OUTPUT);
    GPIO_Set   (MAX7219_CS_GPIO,   1);
    GPIO_Config(MAX7219_SCLK_GPIO, GPIO_FUNC(MAX7219_GPIO_FUNC));
    GPIO_Config(MAX7219_MOSI_GPIO, GPIO_FUNC(MAX7219_GPIO_FUNC));
    GPIO_Config(MAX7219_MISO_GPIO, GPIO_FUNC(MAX7219_GPIO_FUNC));

    GPSBOpenParam_t p = {
        .uiSdo = MAX7219_MOSI_GPIO, 
        .uiSdi = MAX7219_MISO_GPIO, 
        .uiSclk = MAX7219_SCLK_GPIO,
        .uiIsSlave = GPSB_MASTER_MODE, 
        .uiDmaBufSize = 0, 
        .pDmaAddrTx = NULL, .pDmaAddrRx = NULL, .fbCallback = NULL, .pArg = NULL
    };
    if (GPSB_Open(MAX7219_CHANNEL, p) != SAL_RET_SUCCESS) return; 

    GPSB_SetBpw  (MAX7219_CHANNEL, 16);
    GPSB_SetSpeed(MAX7219_CHANNEL, 1000000); 
    GPSB_CsInit  (MAX7219_CHANNEL, MAX7219_CS_GPIO, FALSE); 

    max7219_send(0x0F, 0x00); // 테스트 모드 off
    max7219_send(0x0C, 0x01); // 셧다운 해제(동작 시작)
    max7219_send(0x0B, 0x07); // 스캔 자리 수 8개
    max7219_send(0x0A, 0x08); // 밝기 설정
    max7219_send(0x09, 0x00); // 디코더 off

    for (uint8_t r=1; r<=8; ++r) max7219_send(r, 0x00); // clear
}

static const uint8_t FONT_TOPST[][6] = {
    {0x01,0x01,0x7F,0x01,0x01,0x00}, // T
    {0x3E,0x41,0x41,0x41,0x3E,0x00}, // O
    {0x7F,0x09,0x09,0x09,0x06,0x00}, // P
    {0x26,0x49,0x49,0x49,0x32,0x00}, // S
    {0x01,0x01,0x7F,0x01,0x01,0x00}, // T
};

static uint8_t cols[6 * 5]; // TOPST 전체 열들을 연속한 1차원 배열에 담음
static int ncols;

void draw_window(int idx) // 열을 행으로 바꿔줌
{
    uint8_t rows[8] = {0};
    for (int col=0; col<8; ++col) {                        
        uint8_t c = cols[(idx + col) % ncols];             
        for (int r=0; r<8; ++r)                            
            if (c & (1u<<r)) rows[r] |= (1u << (7 - col)); 
    }
    for (uint8_t r=0; r<8; ++r) max7219_send(r+1, rows[r]);
}


void Dot_Matrix_Run(void)
{
    ncols = 0;
    for (int ch=0; ch<5; ++ch)
        for (int i=0; i<6; ++i)
            cols[ncols++] = FONT_TOPST[ch][i];

    max7219_init();

    int idx = 0;
    for (;;) {
        draw_window(idx);
        idx = (idx + 1) % ncols; 
        SAL_TaskSleep(120); 
    }
}
