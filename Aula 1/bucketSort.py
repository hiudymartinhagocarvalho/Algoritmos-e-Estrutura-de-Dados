def bucket_sort(arr):
    bucket_count = len(arr)
    buckets = [[] for _ in range(bucket_count)]
    
    for num in arr:
        index = int(num * bucket_count)
        buckets[index].append(num)
    
    sorted_arr = []
    
    for bucket in buckets:
        sorted_arr.extend(sorted(bucket))
    
    return sorted_arr