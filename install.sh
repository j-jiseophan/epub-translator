#!/bin/bash

# 설치 플래그
RESTART_NEEDED=false

# uv 설치 확인 및 설치
if ! command -v uv &> /dev/null; then
    echo "uv가 설치되지 않았습니다. 설치 중..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    RESTART_NEEDED=true
    echo "uv 설치 완료."
else
    echo "uv가 이미 설치되어 있습니다."
fi

# npm 설치 확인 및 설치
if ! command -v npm &> /dev/null; then
    echo "npm이 설치되지 않았습니다. 설치 중..."
    sudo apt update
    sudo apt install -y nodejs npm
    RESTART_NEEDED=true
    echo "npm 설치 완료."
else
    echo "npm이 이미 설치되어 있습니다."
fi

# 도구 설치 후 즉시 실행이 필요한 경우를 대비한 환경 설정
export PATH="$HOME/.cargo/bin:$PATH"

# 백엔드 의존성 설치
echo "백엔드 설정을 시작합니다..."
cd backend
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
deactivate
cd ..

# 프런트엔드 의존성 설치
echo "프런트엔드 설정을 시작합니다..."
cd frontend
npm install
cd ..

# 완료 메시지
echo "현재 날짜와 시간: $(date)"
echo "모든 의존성 설치를 완료했습니다."

# 최종 안내
if [ "$RESTART_NEEDED" = true ]; then
    echo ""
    echo "========================================"
    echo "주의: 새로 설치된 도구를 완벽하게 적용하려면"
    echo "터미널을 재시작하거나 'source ~/.bashrc'를 입력하세요."
    echo "========================================"
fi
