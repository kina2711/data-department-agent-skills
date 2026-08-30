# Zero-landing ingestion

The usual extract writes rows to files in object storage, then loads the files into the warehouse. The intermediate copy costs storage, adds a hop that can fail on its own, and exists mainly because it always has. Streaming the extract through memory as a columnar buffer and writing straight to the warehouse removes it.

## The pattern

Read from the source in bounded batches, accumulate into a columnar buffer in memory, and stream that buffer to the warehouse as the batch fills. Columnar rather than row-oriented because the compression is what makes the memory footprint viable and the load fast; bounded batches because an unbounded read is a memory limit waiting to be found in production.

The saving is real but it is not the main reason to do it. Removing the landing zone removes a stage where files accumulate, permissions drift, and a partial write becomes a partial load that nobody notices until reconciliation.

## What the landing zone was doing for you

It was not only a buffer, and everything it provided has to be replaced deliberately rather than dropped:

- **Replay.** A landed file can be re-loaded after a downstream failure without touching the source. In-memory, the only replay is re-extraction, so the source must tolerate it and the extract must be idempotent by watermark or key.
- **Evidence.** A file with a hash is proof of what was extracted. Without it, record row counts, key ranges and a checksum of the buffer at extraction time; reconciliation needs something to compare against.
- **Debugging.** A malformed row in a file can be opened and read. In memory it is gone by the time the load fails, so the failure path must capture the offending batch rather than only the exception.
- **Backpressure.** Object storage absorbs a fast producer. Memory does not: size the batch against the worker's real memory limit, not against the happy path, and fail the batch rather than the process.

## When not to use it

Keep the landing zone where the source cannot be re-read cheaply, where the raw extract is itself a retention requirement, or where the load target is unreliable enough that replay from file is a routine operation rather than an incident. The pattern optimises a cost that is small in absolute terms; it is not worth paying for it with an unrecoverable pipeline.

## What to verify before claiming it works

Row counts and a key-level reconciliation between source and warehouse for the same window, not a successful exit code. Peak memory measured under the largest real batch, not the average. A deliberate mid-stream failure, to confirm the pipeline resumes without duplicating and without silently skipping the batch it was holding.
