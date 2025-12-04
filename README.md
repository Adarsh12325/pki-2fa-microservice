## PKI 2FA Microservice Workflow ---------------------------->

+---------------------+ +---------------------+
| Instructor / Admin | | Student / Trainee |
| Encrypted Seed File | | RSA Key Pair |
+---------------------+ +---------------------+
| |
| Provide encrypted seed | Generate key pair
v v
+-------------------+ +---------------------+
| Decrypt Seed | | Store Private Key |
| app/decrypt_seed.py| | data/student_private.pem |
+-------------------+ +---------------------+
| |
| Decrypted seed stored |
v |
+-----------------------------+ |
| Dockerized Microservice |<----+
| - FastAPI REST API |
| - Cron Job (logs TOTP) |
+-----------------------------+
|
| Generates TOTP every minute
v
+-----------------------------+
| /cron/last_code.txt |
| Stores TOTP logs |
+-----------------------------+
|
| API Endpoints:
| GET /generate-2fa -> returns TOTP
| POST /verify-2fa -> verify TOTP
| POST /decrypt-seed -> decrypt new seed
v
+-----------------------------+
| Client / Application Layer |
| Can request / verify 2FA |
+-----------------------------+



### Explanation:

1. **Instructor / Admin**: Provides encrypted seed file.  
2. **Student / Trainee**: Generates RSA key pair for encryption/decryption.  
3. **Decrypt Seed**: `app/decrypt_seed.py` decrypts the encrypted seed and stores it in `data/seed.txt`.  
4. **Dockerized Microservice**: Runs the FastAPI server and a cron job that logs TOTP every minute in UTC.  
5. **Cron Job**: `scripts/log_2fa_cron.py` writes TOTP codes to `/cron/last_code.txt`.  
6. **API Endpoints**: Allow clients to generate or verify 2FA codes.  
7. **Client Layer**: Any external client or frontend app can request and verify TOTP codes. 
