# Photo Lab

Start the web app and thumbnail worker together:

```bash
./photo-lab/start.sh
```

From this directory, use `./start.sh`. Open http://127.0.0.1:5000
and upload a JPEG or PNG. Ctrl+C stops both services. If either service
exits, the launcher stops the other and returns a failure status.

The launcher requires Python 3.10+ with pip and venv support. It creates
`.venv` when needed and installs the versions in `requirements.txt`.
The first installation needs internet access.

Before the first run, copy `.env.example` to `.env` and set your bucket,
queue URL, and AWS region. Existing environment variables take precedence.
Use your normal AWS credentials (environment variables, an AWS profile,
or an instance role); do not commit credentials.

Your AWS resources must already exist: an S3 bucket with an object-created
notification for `uploads/` sent to the SQS queue, a queue policy allowing
that bucket to send events (see `1-sqs.yml`), and credentials permitting
S3 GetObject/PutObject and SQS ReceiveMessage/DeleteMessage. The worker
must be able to reach AWS. This command does not provision cloud resources
or configure WireGuard; `2-wireguard.sh` contains manual VPN setup notes.

Set `PHOTO_LAB_HOST` or `PHOTO_LAB_PORT` in `.env` to change the listen address.
This launcher uses Flask's development server for the local lab.
# photo-lab
