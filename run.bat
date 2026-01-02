@echo off
echo.
echo ================================
echo  🤖 Automacao ASSAI - Iniciando
echo ================================
echo.

cd backend

echo Verificando dependencias...
pip install -r requirements.txt

echo.
echo Iniciando servidor Flask...
echo Interface disponivel em: http://localhost:5000
echo.
echo Pressione Ctrl+C para parar o servidor
echo.

python app.py

pause