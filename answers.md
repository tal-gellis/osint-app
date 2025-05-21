# answers.md

## 1. Additional Production-Grade Tests

- Check that the scan works properly when the user enters an invalid domain.  
- Make sure that the results are saved correctly in the database.  
- Verify that the system doesn’t crash when running multiple scans in a row.

## 2. Performance Benchmarking & Optimization

- Measure how long each scan takes from start to finish.  
- Store scan results in a cache or database so repeated scans for the same domain are faster.  
- Set timeouts for external tool execution to avoid long-running scans that block the system.

## 3. Known OSINT Tool Bottlenecks and Mitigations

- `theHarvester` can hit rate limits from external services.  
  To handle that, use retry mechanisms or limit the number of sources used.  
- `amass` sometimes takes a long time on deep scans.  
  You can allow the user to choose between fast or deep scanning modes.  
