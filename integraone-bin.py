#!/usr/bin/env python3

__import__('os').environ['TZ'] = 'UTC'
import integraone

if __name__ == "__main__":
    integraone.system.run()