# Jingles

Play music when a request has been made. Modify `secrets.py` to change which jingle plays.

### The jingle format

Jingles are composed of lines of notes. Accompanying the note is a duration (in seconds). There are three valid kinds of notes:

1. Frequency: `147 0.2`
2. Note:      `D4 0.4`
3. Rest:      `rest 0.5`

Notes can also be followed by comments. Jingle files can be dense and hard to parse (especially when it's just a bunch of frequencies), so I'd recommend commenting your jingles, pointing out specific parts of them:

`147 0.2 # This is the part of the song that sounds rly cool`

These notes compose a jingle, which looks something like this:

```
C4 0.1 # 'Ready' sound. This plays a scale.
D4 0.1
E4 0.1
F4 0.1
G4 0.1
A4 0.1
B4 0.1
C5 0.2
```

There is ZERO error handling on this, so if you mess up, the client WILL crash.
