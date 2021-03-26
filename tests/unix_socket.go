package main

import (
	"fmt"
	"net"
	"os"
	"time"
)

func listen(end chan<- bool) {
	addr, err := net.ResolveUnixAddr("unix", "/tmp/foobar")
	if err != nil {
		fmt.Printf("Failed to resolve: %v\n", err)
		os.Exit(1)
	}

	list, err := net.ListenUnix("unix", addr)
	if err != nil {
		fmt.Printf("failed to listen: %v\n", err)
		os.Exit(1)
	}
	conn, _ := list.AcceptUnix()

	buf := make([]byte, 2048)
	n, uaddr, err := conn.ReadFromUnix(buf)
	if err != nil {
		fmt.Printf("LISTEN: Error: %v\n", err)
	} else {
		fmt.Printf("LISTEN: received %v bytes from %+v\n", n, uaddr)
		fmt.Printf("LISTEN: %v\n", string(buf))
	}
	
	conn.Close()
	list.Close()
	end <- true
}

func dial(end chan<- bool) {
	addr, err := net.ResolveUnixAddr("unix", "/tmp/foobar")
	if err != nil {
		fmt.Printf("Failed to resolve: %v\n", err)
		os.Exit(1)
	}

	conn, err := net.DialUnix("unix", nil, addr)
	if err != nil {
		fmt.Printf("Failed to dial: %v\n", err)
		os.Exit(1)
	}

	if i, err := conn.Write([]byte("Test message")); err != nil {
		fmt.Printf("DIAL: Error: %v\n", err)
	} else {
		fmt.Printf("DIAL: Success, sent %v bytes\n", i)
	}

	conn.Close()
	end <- true
}

func main() {
	end := make(chan bool, 2)
	go listen(end)
	time.Sleep(time.Second)
	go dial(end)
	<-end
	<-end
}