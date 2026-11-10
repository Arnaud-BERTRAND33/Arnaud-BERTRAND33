pkill -f demo_backend.py; sleep 1
cd /home/user/ten-assistant/moteur && rm -f /tmp/ten-ia.log
TEN_DELAI=2.5 TEN_RESET=1 TEN_DEV_DONNEES=/tmp/claude-0/-home-user-Arnaud-BERTRAND33/e0d2ae79-0b90-55c9-8978-3eac4231f1aa/scratchpad/donnees nohup .venv/bin/python /tmp/claude-0/-home-user-Arnaud-BERTRAND33/e0d2ae79-0b90-55c9-8978-3eac4231f1aa/scratchpad/demo_backend.py > /tmp/claude-0/-home-user-Arnaud-BERTRAND33/e0d2ae79-0b90-55c9-8978-3eac4231f1aa/scratchpad/backend.log 2>&1 &
for i in $(seq 1 60); do curl -s -H 'X-TEN-Jeton: dev' 127.0.0.1:8765/api/etat | grep -q '"pret"' && break; sleep 2; done
curl -s -H 'X-TEN-Jeton: dev' 127.0.0.1:8765/api/etat
