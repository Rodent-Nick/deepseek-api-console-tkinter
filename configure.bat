@ECHO OFF
REM This Batch script installs dependency for ds_api_console.pyw.
REM It depends on some built-in libs and an external lib OpenAI SDK.
:start
ECHO YOU ARE ABOUT TO INSTALL OpenAI PYTHON SDK. PROCEED? 
SET choice=
SET /p choice=TYPE 'Y' TO CONTINUE (CASE-SENSITIVE): 
IF '%choice%'=='' GOTO start
IF '%choice%'=='Y' GOTO install
ECHO YOU'VE CANCELLED THIS INSTALLATION.
PAUSE
EXIT
:install
pip install openai -i https://pypi.tuna.tsinghua.edu.cn/simple
CLEAR
ECHO INSTALLATION COMPLETED.
PAUSE
EXIT