def fill_length(m):

    expected_size = 10
    cur_size = len(m)
    for i in range(expected_size-cur_size):
        m+='0'
    return m

