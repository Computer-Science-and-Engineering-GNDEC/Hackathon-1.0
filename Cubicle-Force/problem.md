### Mail server and Web based mail client 

Features required:
1. Full-featured mail server
2. Single Sign In(SSO) for authentication
3. Password recovery through sms.
4. Password recovery through alternative email.
5. A full-set smtp email server(Postfix)
6. Secure IMAP and POP3 email server(e.g Dovecot)
7. Rspamd : anti-spam filter with SPF, DKIM, DMARC, ARC, ratelimit and greylisting capabilities
8. Clamav : antivirus with automatic updates and third-party signature databases
9. Zeyple : automatic GPG encryption of all your emails
10. Sieve : email filtering (vacation auto-responder, auto-forward, etc...)
11. Fetchmail : fetch emails from external IMAP/POP3 server into local mailbox
12. Web based email client, best suited to this requirement.
13. Postfixadmin : web-based administration interface
14. Unbound: recursive caching DNS resolver with DNSSEC support
15. NSD : authoritative DNS server with DNSSEC support
16. Træfik : modern HTTP reverse proxy
17. SSL : let's encrypt with auto-renewal (SAN and wildcard certificates), custom and self-signed certificates support
18. OpenLDAP :  ldap support 
19. Supporting multiple virtual domains over MySQL/PostgreSQL backend
20. Integration tests with Travis CI



### Start-up Management:
 
*Software to manage accounts / work of service startup (to be unicorn)*

Background material:

(https://docs.erpnext.com/docs/user/manual/en/selling/articles/erpnext-for-services-organization)
(https://docs.erpnext.com/docs/user/videos/learn/services)
