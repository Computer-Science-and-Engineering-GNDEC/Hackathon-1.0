## Hosting the best email solution available (Mail server and Web based mail client)

We have choosen [Mailcow](https://github.com/mailcow/mailcow-dockerized/) and it satisfies following requirements mentioned in problem statement:

- Full-featured mail server
- A full-set smtp email server(Postfix)
- Secure IMAP and POP3 email server(e.g Dovecot)
- Rspamd : anti-spam filter with SPF, DKIM, DMARC, ARC, ratelimit and greylisting capabilities
- Clamav : antivirus with automatic updates and third-party signature databases
- Encryption of all your emails
- Email filtering (vacation auto-responder, auto-forward, etc…)
- imapsync : fetch emails from external IMAP/POP3 server into local mailbox
- Web based email client, best suited to this requirement.
- Unbound: recursive caching DNS resolver with DNSSEC support
- Træfik : modern HTTP reverse proxy
- SSL : let’s encrypt with auto-renewal (SAN and wildcard certificates), custom and self-signed certificates support
- Supporting multiple virtual domains over MySQL/PostgreSQL backend

And much more than this:
- Memcached
- Solr
- Redis
- 2FA, TOTP
- REST API
...


# Hosted Instance:

Its Admin interface is accessible at: https://surajdadral.me/   
And mail interface is accessible at: https://surajdadral.me/SOGo  (Test user: test@mail.surajdadral.me    Password: test@123)

