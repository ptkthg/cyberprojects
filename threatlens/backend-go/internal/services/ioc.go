package services

import (
	"regexp"
	"strings"
)

func NormalizeIOC(raw string) string {
	value := strings.TrimSpace(raw)
	value = strings.ReplaceAll(value, "[.]", ".")
	return value
}

func DetectIOCType(ioc string) string {
	if regexp.MustCompile(`^\d{1,3}(\.\d{1,3}){3}$`).MatchString(ioc) {
		return "ipv4"
	}
	if regexp.MustCompile(`^[a-fA-F0-9]{32}$`).MatchString(ioc) {
		return "md5"
	}
	if regexp.MustCompile(`^[a-fA-F0-9]{40}$`).MatchString(ioc) {
		return "sha1"
	}
	if regexp.MustCompile(`^[a-fA-F0-9]{64}$`).MatchString(ioc) {
		return "sha256"
	}
	if strings.HasPrefix(ioc, "http://") || strings.HasPrefix(ioc, "https://") {
		return "url"
	}
	if regexp.MustCompile(`^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`).MatchString(ioc) {
		return "domain"
	}
	return "unknown"
}

func BuildKQL(ioc, iocType string) string {
	switch iocType {
	case "ipv4":
		return "DeviceNetworkEvents | where RemoteIP == \"" + ioc + "\""
	case "domain":
		return "DeviceNetworkEvents | where RemoteUrl has \"" + ioc + "\""
	case "url":
		return "DeviceNetworkEvents | where RemoteUrl == \"" + ioc + "\""
	default:
		return "DeviceFileEvents | where SHA256 == \"" + ioc + "\""
	}
}
