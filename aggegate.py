
def aggreate_data(data):
    """Aggregates the data by protocol and returns the results"""
    # Initialize the variables
    udp_count = 0
    tcp_count = 0
    udp_data_size = 0
    tcp_data_size = 0

    # Iterate through the data
    for entry in data:
        if entry['protocol'] == 'UDP':
            udp_count += 1
            udp_data_size += entry['data_size_kb']
        elif entry['protocol'] == 'TCP':
            tcp_count += 1
            tcp_data_size += entry['data_size_kb']
            
    return udp_count, tcp_count, udp_data_size, tcp_data_size