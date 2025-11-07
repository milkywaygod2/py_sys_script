"""
Network Utilities
네트워크 유틸리티

This module provides utility functions for network operations.
네트워크 작업을 위한 유틸리티 함수들을 제공합니다.
"""

import socket
import subprocess
import time
from typing import Optional, Tuple


def check_port_open(host: str, port: int, timeout: float = 3.0) -> bool:
    '''
    Check if a port is open on a host. 호스트의 포트가 열려있는지 확인합니다.
    Args:
    host: Host address 호스트 주소
    port: Port number 포트 번호
    timeout: Connection timeout in seconds 연결 타임아웃 (초)
    Returns:
    True if port is open, False otherwise 포트가 열려있으면 True, 아니면 False
    '''
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def ping_host(host: str, count: int = 4) -> Tuple[bool, float]:
    '''
    Ping a host and return success status and average response time. 호스트를 핑하고 성공 여부와 평균 응답 시간을 반환합니다.
    Args:
    host: Host address to ping 핑할 호스트 주소
    count: Number of ping attempts 핑 시도 횟수
    Returns:
    Tuple of (success, average_time_ms) (성공 여부, 평균 시간 ms) 튜플
    '''
    import platform
    import re
    
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, str(count), host]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Extract average time from output
            if platform.system().lower() == 'windows':
                match = re.search(r'Average = (\d+)ms', result.stdout)
            else:
                match = re.search(r'avg[^=]*=\s*([0-9.]+)', result.stdout)
            
            if match:
                avg_time = float(match.group(1))
                return True, avg_time
            return True, 0.0
        
        return False, 0.0
    except Exception:
        return False, 0.0


def get_local_ip() -> Optional[str]:
    '''
    Get local IP address. 로컬 IP 주소를 가져옵니다.
    Returns:
    Local IP address or None if error 로컬 IP 주소, 에러시 None
    '''
    try:
        # Create a socket and connect to external server
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(('8.8.8.8', 80))
        local_ip = sock.getsockname()[0]
        sock.close()
        return local_ip
    except Exception:
        return None


def get_hostname() -> Optional[str]:
    '''
    Get system hostname. 시스템 호스트명을 가져옵니다.
    Returns:
    Hostname or None if error 호스트명, 에러시 None
    '''
    try:
        return socket.gethostname()
    except Exception:
        return None


def resolve_hostname(hostname: str) -> Optional[str]:
    '''
    Resolve hostname to IP address. 호스트명을 IP 주소로 해석합니다.
    Args:
    hostname: Hostname to resolve 해석할 호스트명
    Returns:
    IP address or None if error IP 주소, 에러시 None
    '''
    try:
        return socket.gethostbyname(hostname)
    except Exception:
        return None


def get_reverse_dns(ip_address: str) -> Optional[str]:
    '''
    Get hostname from IP address (reverse DNS lookup). IP 주소에서 호스트명을 가져옵니다 (역방향 DNS 조회).
    Args:
    ip_address: IP address IP 주소
    Returns:
    Hostname or None if error 호스트명, 에러시 None
    '''
    try:
        return socket.gethostbyaddr(ip_address)[0]
    except Exception:
        return None


def check_internet_connection(test_host: str = '8.8.8.8', timeout: float = 3.0) -> bool:
    '''
    Check if internet connection is available. 인터넷 연결이 가능한지 확인합니다.
    Args:
    test_host: Host to test connection 연결 테스트할 호스트
    timeout: Connection timeout in seconds 연결 타임아웃 (초)
    Returns:
    True if connected, False otherwise 연결되면 True, 아니면 False
    '''
    return check_port_open(test_host, 53, timeout)


def scan_ports(host: str, start_port: int, end_port: int) -> list:
    '''
    Scan range of ports on a host. 호스트의 포트 범위를 스캔합니다.
    Args:
    host: Host address 호스트 주소
    start_port: Starting port number 시작 포트 번호
    end_port: Ending port number 종료 포트 번호
    Returns:
    List of open ports 열린 포트 리스트
    '''
    open_ports = []
    
    for port in range(start_port, end_port + 1):
        if check_port_open(host, port, timeout=1.0):
            open_ports.append(port)
    
    return open_ports


def measure_download_speed(url: str = 'http://speedtest.tele2.net/1MB.zip',
                           timeout: int = 30) -> Optional[float]:
    '''
    Measure download speed in Mbps. 다운로드 속도를 Mbps로 측정합니다.
    Args:
    url: URL to download for testing 테스트용 다운로드 URL
    timeout: Download timeout in seconds 다운로드 타임아웃 (초)
    Returns:
    Download speed in Mbps or None if error 다운로드 속도 (Mbps), 에러시 None
    '''
    import urllib.request
    
    try:
        start_time = time.time()
        
        with urllib.request.urlopen(url, timeout=timeout) as response:
            data = response.read()
        
        end_time = time.time()
        
        # Calculate speed
        duration = end_time - start_time
        size_mb = len(data) / (1024 * 1024)
        speed_mbps = (size_mb * 8) / duration
        
        return round(speed_mbps, 2)
    except Exception:
        return None


def get_network_interfaces() -> dict:
    '''
    Get information about network interfaces. 네트워크 인터페이스 정보를 가져옵니다.
    Returns:
    Dictionary with interface information 인터페이스 정보 딕셔너리
    '''
    import platform
    
    interfaces = {}
    
    try:
        if platform.system().lower() == 'windows':
            result = subprocess.run(['ipconfig', '/all'], 
                                  capture_output=True, text=True)
        else:
            result = subprocess.run(['ifconfig'], 
                                  capture_output=True, text=True)
        
        interfaces['raw_output'] = result.stdout
        interfaces['hostname'] = get_hostname()
        interfaces['local_ip'] = get_local_ip()
    except Exception:
        pass
    
    return interfaces
