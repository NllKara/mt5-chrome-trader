@echo off
REG ADD "HKCU\Software\Google\Chrome\NativeMessagingHosts\com.ftc.mt5trader" /ve /t REG_SZ /d "C:\\MT5ChromeTrader\\native\\com.ftc.mt5trader.json" /f
echo Native host registered.
pause
