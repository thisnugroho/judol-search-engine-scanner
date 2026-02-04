import hashlib
import time
import uuid

class Cap:
    def __init__(self, difficulty=4, count=50, verify_window=300):
        self.difficulty = difficulty
        self.count = count  
        self.verify_window = verify_window
        # Simple in-memory storage for tokens (use Redis in production)
        self.tokens = {}

    def create_challenge(self):
        token = str(uuid.uuid4())
        # salt_seed logic: JS uses it as length in prng(seed, length).
        # To get random salt for each token, token itself is part of PRNG seed.
        # But `s` tells how long the salt should be.
        salt_len = 16 
        
        self.tokens[token] = {
            'c': self.count,
            's': salt_len,
            'd': self.difficulty,
            'ts': time.time()
        }
        
        return {
            'token': token,
            'challenge': {
                'c': self.count,
                's': salt_len,
                'd': self.difficulty
            }
        }

    def verify(self, token, solutions):
        if token not in self.tokens:
            return {'success': False, 'error': 'Invalid or expired token'}
            
        data = self.tokens[token]
        
        if time.time() - data['ts'] > self.verify_window:
            del self.tokens[token]
            return {'success': False, 'error': 'Challenge expired'}

        if len(solutions) != data['c']:
             return {'success': False, 'error': 'Incorrect number of solutions'}

        # Verify challenges
        c = data['c']
        s = data['s']
        d = data['d']
        
        try:
            for i in range(c):
                # Reconstruct salt and target
                idx = i + 1
                salt_seed = f"{token}{idx}"
                target_seed = f"{token}{idx}d"
                
                salt = self._prng(salt_seed, int(s)) 
                target = self._prng(target_seed, int(d))
                # JS call: prng(`${token}${i}`, challenge.s)
                # Wait, looking at JS code again:
                # challenge.s is the SALT SEED?
                # Line 196: const { challenge, token } = ...
                # Line 207: challenges = Array.from({ length: challenge.c }, ...
                # Line 211: prng(`${token}${i}`, challenge.s)
                # Line 212: prng(`${token}${i}d`, challenge.d)
                
                # `challenge.s` in JS seems to be used as LENGTH because prng(seed, length).
                # But `challenge.s` is usually a string salt in other PoW.
                # Let's check `prng` signature: function prng(seed, length)
                # So `challenge.s` MUST be an INTEGER logic-wise for it to be length?
                # OR `challenge.s` is passed as is.
                # If `challenge.s` is a string "somesalt", prng uses "somesalt" as length? 
                # JS `result.length < length`. "somesalt".length? No.
                # If `length` is string, it's converted to number? 
                # In JS `while (result.length < length)` -> if length is string, it compares string length?
                # No, number.
                
                # WAIT. In JS:
                # `const { challenge, token } = response`
                # If I send: challenge: { c: 100, s: 8, d: 4 }
                # Then `prng(seed, 8)` -> 8 chars hex string.
                # So `s` and `d` in the challenge object are LENGTHS.
                
                
                salt = self._prng(salt_seed, int(s)) 
                target = self._prng(target_seed, int(d))
                
                solution = solutions[i]
                # JS nonce is number.
                # Worker: inputString = salt + nonce
                # Hash match check.
                
                check = f"{salt}{solution}"
                hashed = hashlib.sha256(check.encode('utf-8')).hexdigest()
                
                if not hashed.startswith(target):
                    return {'success': False, 'error': f'Invalid solution at index {i}'}
                    
            # All good
            del self.tokens[token] # Consumed
            
            # Generate response token (can be same or new)
            return {
                'success': True, 
                'token': token,
                'expires': datetime_to_iso(time.time() + 3600)
            }
            
        except Exception as e:
            print(e)
            return {'success': False, 'error': str(e)}

    def _prng(self, seed_str, length):
        def fnv1a(s):
            h = 2166136261
            for char in s:
                h ^= ord(char)
                # h += (h << 1) + (h << 4) + (h << 7) + (h << 8) + (h << 24)
                # Equivalent to: h * 16777619
                # But let's follow JS bitwise operations exactly to be safe
                # Note: Python ints are not 32-bit.
                h = (h * 16777619) & 0xFFFFFFFF
            return h

        state = fnv1a(seed_str)
        result = ""
        
        while len(result) < length:
            # Xorshift32
            # state ^= state << 13
            state = (state ^ (state << 13)) & 0xFFFFFFFF
            # state ^= state >>> 17
            state = (state ^ (state >> 17)) & 0xFFFFFFFF
            # state ^= state << 5
            state = (state ^ (state << 5)) & 0xFFFFFFFF
            
            # hex conversion
            # rnd.toString(16).padStart(8, "0")
            hex_val = format(state, '08x')
            result += hex_val
            
        return result[:length]

def datetime_to_iso(timestamp):
    from datetime import datetime, timezone
    return datetime.fromtimestamp(timestamp, timezone.utc).isoformat().replace('+00:00', 'Z')
