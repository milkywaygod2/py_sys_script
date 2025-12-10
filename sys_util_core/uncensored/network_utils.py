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

from sys_util_core.jsystems import CmdSystem, LogSystem


"""
@brief	Check if a port is open on a host. 호스트의 포트가 열려있는지 확인합니다.
@param	host	Host address 호스트 주소
@param	port	Port number 포트 번호
@param	timeout	Connection timeout in seconds 연결 타임아웃 (초)
@return	True if port is open, False otherwise 포트가 열려있으면 True, 아니면 False
"""
def check_port_open(
		host: str,
		port: int,
		timeout: float = 3.0
 	) -> bool:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


"""
@brief	Ping a host and return success status and average response time. 호스트를 핑하고 성공 여부와 평균 응답 시간을 반환합니다.
@param	host	Host address to ping 핑할 호스트 주소
@param	count	Number of ping attempts 핑 시도 횟수
@return	Tuple of (success, average_time_ms) (성공 여부, 평균 시간 ms) 튜플
"""
def ping_host(host: str, count: int = 4) -> Tuple[bool, float]:
    import platform
    import re
    
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, str(count), host]
    
    try:
        returncode_with_msg = CmdSystem.run(command, timeout=30)
        
        if returncode_with_msg[0] != 0:
            raise Exception("Ping command failed")
            
        # Extract average time from output
        if platform.system().lower() == 'windows':
            match = re.search(r'Average = (\d+)ms', returncode_with_msg[1])
        else:
            match = re.search(r'avg[^=]*=\s*([0-9.]+)', returncode_with_msg[1])
        
        return True, float(match.group(1)) if match else 0.0
        
    except Exception as e:
        LogSystem.log_error(f"Ping failed: {e}")
        return False, 0.0


"""
@brief	Get local IP address. 로컬 IP 주소를 가져옵니다.
@return	Local IP address or None if error 로컬 IP 주소, 에러시 None
"""
def get_local_ip() -> Optional[str]:
    try:
        # Create a socket and connect to external server
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(('8.8.8.8', 80))
        local_ip = sock.getsockname()[0]
        sock.close()
        return local_ip
    except Exception:
        return None


"""
@brief	Get system hostname. 시스템 호스트명을 가져옵니다.
@return	Hostname or None if error 호스트명, 에러시 None
"""
def get_hostname() -> Optional[str]:
    try:
        return socket.gethostname()
    except Exception:
        return None


"""
@brief	Resolve hostname to IP address. 호스트명을 IP 주소로 해석합니다.
@param	hostname	Hostname to resolve 해석할 호스트명
@return	IP address or None if error IP 주소, 에러시 None
"""
def resolve_hostname(hostname: str) -> Optional[str]:
    try:
        return socket.gethostbyname(hostname)
    except Exception:
        return None


"""
@brief	Get hostname from IP address (reverse DNS lookup). IP 주소에서 호스트명을 가져옵니다 (역방향 DNS 조회).
@param	ip_address	IP address IP 주소
@return	Hostname or None if error 호스트명, 에러시 None
"""
def get_reverse_dns(ip_address: str) -> Optional[str]:
    try:
        return socket.gethostbyaddr(ip_address)[0]
    except Exception:
        return None


"""
@brief	Check if internet connection is available. 인터넷 연결이 가능한지 확인합니다.
@param	test_host	Host to test connection 연결 테스트할 호스트
@param	timeout	    Connection timeout in seconds 연결 타임아웃 (초)
@return	True if connected, False otherwise 연결되면 True, 아니면 False
"""
def check_internet_connection(test_host: str = '8.8.8.8', timeout: float = 3.0) -> bool:
    return check_port_open(test_host, 53, timeout)


"""
@brief	Scan range of ports on a host. 호스트의 포트 범위를 스캔합니다.
@param	host	    Host address 호스트 주소
@param	start_port	Starting port number 시작 포트 번호
@param	end_port	Ending port number 종료 포트 번호
@return	List of open ports 열린 포트 리스트
"""
def scan_ports(
		host: str,
		start_port: int,
		end_port: int
 	) -> list:
    open_ports = []
    
    for port in range(start_port, end_port + 1):
        if check_port_open(host, port, timeout=1.0):
            open_ports.append(port)
    
    return open_ports


"""
@brief	Measure download speed in Mbps. 다운로드 속도를 Mbps로 측정합니다.
@param	url	    URL to download for testing 테스트용 다운로드 URL
@param	timeout	Download timeout in seconds 다운로드 타임아웃 (초)
@return	Download speed in Mbps or None if error 다운로드 속도 (Mbps), 에러시 None
"""
def measure_download_speed(url: str = 'http://speedtest.tele2.net/1MB.zip',
                           timeout: int = 30) -> Optional[float]:
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


"""
@brief	Get information about network interfaces. 네트워크 인터페이스 정보를 가져옵니다.
@return	Dictionary with interface information 인터페이스 정보 딕셔너리
"""
def get_network_interfaces() -> dict:
    import platform
    
    interfaces = {}
    
    try:
        cmd = ['ipconfig', '/all'] if platform.system().lower() == 'windows' else ['ifconfig']
        returncode_with_msg = CmdSystem.run(cmd)
        interfaces['raw_output'] = returncode_with_msg[1]
        interfaces['hostname'] = get_hostname()
        interfaces['local_ip'] = get_local_ip()
    except Exception:
        pass
    
    return interfaces
