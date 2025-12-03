import hashlib

emails = [
    "nishant.parekh@unilever.com",
    "semih.sakir@unilever.com", 
    "ajab.niazi@hbr.org", 
    "chris@ycombinator.com", 
    "tom@ycombinator.com", 
    "jh@ycombinator.com", 
    "ankit@ycombinator.com", 
    "eli@ycombinator.com", 
    "lauren@ycombinator.com", 
    "andrew@ycombinator.com"
]

for email in emails:
    email_hash = hashlib.sha256(email.encode()).hexdigest()
    print(email_hash)

