
# TODO: modification: replace date
# TODO: modification: switch order of two lines
# TODO: modification: change name of the sstable nb-2-big to nb-5.big for example
sample_log_output = """
WARN  [main] 2023-12-05 09:38:00,832 NativeLibrary.java:199 - Unable to lock JVM memory (ENOMEM). This can result in part of the JVM being swapped out, especially with mmapped I/O enabled. Increase RLIMIT_MEMLOCK.
INFO  [ScheduledTasks:1] 2023-12-05 09:38:00,845 StreamManager.java:260 - Storing streaming state for 3d or for 119156 elements
INFO  [main] 2023-12-05 09:38:00,914 MonotonicClock.java:208 - Scheduling approximate time conversion task with an interval of 10000 milliseconds
INFO  [main] 2023-12-05 09:38:00,924 MonotonicClock.java:344 - Scheduling approximate time-check task with a precision of 2 milliseconds
INFO  [main] 2023-12-05 09:38:01,002 StartupChecks.java:203 - jemalloc seems to be preloaded from /usr/local/lib/libjemalloc.so
WARN  [main] 2023-12-05 09:38:01,003 StartupChecks.java:257 - JMX is not enabled to receive remote connections. Please see cassandra-env.sh for more info.
INFO  [main] 2023-12-05 09:38:01,006 SigarLibrary.java:46 - Initializing SIGAR library
WARN  [main] 2023-12-05 09:38:01,019 SigarLibrary.java:172 - Cassandra server running in degraded mode. Is swap disabled? : false,  Address space adequate? : true,  nofile limit adequate? : true, nproc limit adequate? : true 
WARN  [main] 2023-12-05 09:38:01,020 StartupChecks.java:492 - Maximum number of memory map areas per process (vm.max_map_count) 65530 is too low, recommended value: 1048575, you can change it with sysctl.
INFO  [main] 2023-12-05 09:38:02,114 Keyspace.java:381 - Creating replication strategy system params KeyspaceParams{durable_writes=true, replication=ReplicationParams{class=org.apache.cassandra.locator.LocalStrategy}}
INFO  [main] 2023-12-05 09:38:02,204 ColumnFamilyStore.java:484 - Initializing system.IndexInfo
INFO  [SSTableBatchOpen:2] 2023-12-05 09:38:03,484 BufferPools.java:49 - Global buffer pool limit is 512.000MiB for chunk-cache and 128.000MiB for networking
INFO  [SSTableBatchOpen:1] 2023-12-05 09:38:03,507 SSTableReaderBuilder.java:354 - Opening /var/lib/cassandra/data/system/IndexInfo-9f5c6374d48532299a0a5094af9ad1e3/nb-2-big (0.035KiB)
INFO  [SSTableBatchOpen:2] 2023-12-05 09:38:03,507 SSTableReaderBuilder.java:354 - Opening /var/lib/cassandra/data/system/IndexInfo-9f5c6374d48532299a0a5094af9ad1e3/nb-1-big (0.057KiB)
INFO  [main] 2023-12-05 09:38:03,557 CacheService.java:101 - Initializing key cache with capacity of 100 MiBs.
INFO  [main] 2023-12-05 09:38:03,622 CacheService.java:123 - Initializing row cache with capacity of 0 MiBs
INFO  [main] 2023-12-05 09:38:03,625 CacheService.java:152 - Initializing counter cache with capacity of 50 MiBs
"""

sample_npe_stack_trace = """
Exception in thread "main" java.lang.NullPointerException
    at com.example.MyClass.methodA(MyClass.java:15)
    at com.example.MyClass.methodB(MyClass.java:20)
    at com.example.MyClass.methodC(MyClass.java:25)
    at com.example.AnotherClass.methodD(AnotherClass.java:30)
    at com.example.AnotherClass.methodE(AnotherClass.java:35)
    at com.example.YetAnotherClass.methodF(YetAnotherClass.java:40)
    at com.example.YetAnotherClass.methodG(YetAnotherClass.java:45)
    at com.example.FinalClass.methodH(FinalClass.java:50)
    at com.example.FinalClass.methodI(FinalClass.java:55)
    at com.example.Application.main(Application.java:60)
"""

sample_npe_stack_trace_with_line_changes = """
Exception in thread "main" java.lang.NullPointerException
    at com.example.MyClass.methodA(MyClass.java:15)
    at com.example.MyClass.methodB(MyClass.java:20)
    at com.example.MyClass.methodC(MyClass.java:25)
    at com.example.AnotherClass.methodD(AnotherClass.java:31)
    at com.example.AnotherClass.methodE(AnotherClass.java:35)
    at com.example.YetAnotherClass.methodF(YetAnotherClass.java:40)
    at com.example.YetAnotherClass.methodG(YetAnotherClass.java:46)
    at com.example.FinalClass.methodH(FinalClass.java:50)
    at com.example.FinalClass.methodI(FinalClass.java:55)
    at com.example.Application.main(Application.java:60)
"""

different_npe_stack_trace = """
Exception in thread "main" java.lang.NullPointerException
    at com.example.MyClass.methodA(MyClass.java:15)
    at com.example.MyClass.methodB(MyClass.java:20)
    at com.example.MyClass.methodC(MyClass.java:25)
    at com.example.AnotherClass.methodD(AnotherClass.java:30)
    at com.example.AnotherClass.methodE(AnotherClass.java:35)
    at com.example.YetAnotherClass.methodX(YetAnotherClass.java:42)
    at com.example.FinalClass.methodH(FinalClass.java:50)
    at com.example.FinalClass.methodI(FinalClass.java:55)
    at com.example.Application.main(Application.java:60)
"""