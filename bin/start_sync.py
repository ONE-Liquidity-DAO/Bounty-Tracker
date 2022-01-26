#!/usr/bin/env python3
'''
Starts the tracker and the sync script
'''
import asyncio
from tracker.sync.sync_main import main

asyncio.run(main())
