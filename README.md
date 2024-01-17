# Socket programming
`socket` 本質上是一種 **IPC** (`Inter-Process Communication`) 的技術，用於**兩個或多個** `process` 進行資料交換或者通訊。

在網路領域，`socket` 著重的不是同一台主機間 `process` 的通訊，而是不同主機執行的 `process` 互相交換資料的通訊。

我們在寫 `socket programming` 的時候會使用 `os` 提供的 `API`，來避免重複造輪子，今天的筆記會簡單介紹一下 `linux` 提供的 `socket API`和`python` 提供的 `socket API`，並用兩個簡單的範例介紹如何用 `tcp` 跟 `udp` 協定透過 `socket` 傳輸資料。

linux在寫 `socket` 相關的程式的時候，需要先

```c
#include <arpa/inet.h>  // sockaddr 相關
#include <sys/socket.h>
```

python在寫 `socket` 相關的程式的時候，需要先
```python=
import socket
```

## C Socket Function Introduction
### socket(int, int, int)
使用socket(int ,int ,int )在kernel中建立一個socket，並傳回該socket的檔案描述符
```c
int socket(int domain, int type, int protocol)
```

**domain**

定義要建立哪一種類型的 `socket`，常用的有以下幾種類型
- **AF_UNIX**, **AF_LOCAL**: 用於本機間 `process` 的溝通   
- **AF_INET**, **AF_INET6**
    - **AF_INET**: IPv4 協定
    - **AF_INET6**: IPv6 協定

詳細的選項可以參考 `socket` 的 [man page](https://man7.org/linux/man-pages/man2/socket.2.html)

**type**

`socket` 傳輸資料的手段(`communication semantics`)

- **SOCK_STREAM**: 對應到 `tcp` 協定
- **SOCK_DGRAM**: 對應到 `udp` 協定

**protocol**

設定通訊協定的號碼，通常在寫的時候會填入 `0`，`kernel` 會根據上面的兩個參數自動選擇合適的協定。

- [protocol man page](https://man7.org/linux/man-pages/man5/protocols.5.html#top_of_page)

`/etc/protocols` 可以看到 `linux` 底下支援的協定

**Return Value**

成功建立 `socket` 之後，此函式會返回該 `socket` 的**檔案描述符**(`socket file descriptor`)，在之後的操作可以透過這個回傳值來操作我們建立的 `socket`。 如果建立失敗則會回傳 `-1(INVALID_SOCKET)`


### connect(int, struct sockaddr_in, int)
處理網路服務時，如TCP，ClientSocket需與ServerSocket建立連接
TCP Client可以connect()函式與Server端建立連結
```clike
 int connect(int sockfd, struct sockaddr_in  *server, int addr_len);  
```
**sockfd**

sockfd即socket()函數之回傳值，為socket的描述符

**server**

關於這個socket的所有信息
netinet/in.h已經為我們定義好了一個struct sockaddr_in來儲存這些資訊
```clike
// if IPv6 please referense sockaddr_in6
// IPv4 AF_INET sockets:
struct sockaddr_in {
    short            sin_family;   // AF_INET
    unsigned short   sin_port;     // 儲存port number
    struct in_addr   sin_addr; 
    char             sin_zero[8];  // Not used, must be zero
};

struct in_addr {
    unsigned long s_addr;          // load with inet_pton()
};
```
以下為範例
```clike
struct sockaddr_in info;

bzero(&info,sizeof(info));	//初始化 將struct涵蓋的bits設為0
info.sin_family = PF_INET;	//sockaddr_in為Ipv4結構

info.sin_addr.s_addr = inet_addr("123.123.13.12");	//IP address

info.sin_port = htons(8080);

```
常用的有以下這五種
* 只能用在```IPv4```的處理
    * inet_addr
    * inet_aton
    * inet_ntoa
* 兼容```IPv4``` and ```IPv6```
    * inet_pton
    * inet_ntop

**PF_INET ?**

AF = Address Family
PF = Protocol Family
AF_INET = PF_INET
理論上建立socket時是指定協議，應該用PF_xxxx，設置地址時應該用AF_xxxx，但混用不會有太大問題

**inet_addr?**

一般163.23.148.100這種ip地址為ASCII表示法
用inet_addr轉為整數型式ip，其為binary data

**hton ?**

網路端的字節序與本機端的字節序可能不一致 網路端總是用Big endian，而本機端卻要視處理器體系而定，使用的是Little endian。 htons()就是Host TO Network Short integer的縮寫，它將本機端的字節序(endian)轉換成了網路端的字節序

**addr_len**

就是*server的大小

**Return value**

成功回傳0，失敗傳-1

### bind(int, struct sockaddr, unsigned int)
上面介紹了創建一個 socket 的方式，也簡單的介紹了存放 address 的資料結構，一些常用的轉換函式。

接著我們要介紹 bind，這個函式可以讓前面創建的 socket 實際綁定到本機的某個 port 上面，這樣子 client 端在送資料到某個 port 的時候，我們寫的 server 程式才可以在那個 port 上面運行，處理資料。

```clike
int bind(int sockfd, struct sockaddr *addr, unsigned int addrlen)
```

**sockfd**

一開始呼叫 socket() 的回傳值

**addr**

sockaddr 來描述 bind 要綁定的 address 還有 port。

在先前的介紹有簡單提到，實際存放 ip address 的是 sockaddr_in.sin_addr.s_addr，如果今天不想綁定 ip address，而是單單想綁定某個 port 的時候，s_addr 就要設成 INADDR_ANY，通常會出現在你的主機有多個 ip 或者 ip 不是固定的情況。

[INADDR_ANY 參考](https://blog.csdn.net/qq_26399665/article/details/52932755)

**addrlen**

addr 結構的 size

**return**

如果綁定成功就會回傳 0，失敗回傳 -1

**example**

```clike
// 建立 socket, 並且取得 socket_fd
int socket_fd = socket(PF_INET , SOCK_DGRAM , 0);
if (socket_fd < 0) {
    printf("Fail to create a socket.");
}
    
// 地址資訊
struct sockaddr_in serverAddr = {
    .sin_family =AF_INET,             // Ipv4
    .sin_addr.s_addr = INADDR_ANY,    // 沒有指定 ip address
    .sin_port = htons(12000)          // 綁定 port 12000
};

// 綁定
// 因為 bind 可以用在不同種類的 socket，所以是用 sockaddr 宣告
// 我們用於網路的 address，是用 sockaddr_in 這個結構
// 在填入的時候要進行強制轉型
// 前面介紹 sockaddr_in 裡面 sin_zero 就是為了讓兩個結構有相同的 size
if (bind(socket_fd, (const struct sockaddr *)&serverAddr, sizeof(serverAddr)) < 0) {
    perror("Bind socket failed!");
    close(socket_fd);
    exit(0);
}

printf("Server ready!\n");
```


### 參考資料
- [Linux 的 file descriptor 筆記 FD 真的好重要](https://kkc.github.io/2020/08/22/file-descriptor/)
- [Linux 下 socket 通訊所用的 sockfd 怎麼來的](https://www.cnblogs.com/chorm590/p/12745824.html)

## C socket UDP

![](https://i.imgur.com/sxPuuic.png)

接下來就要開始編寫我們的第一支 `socket` 程式，`client` 端輸入小寫的英文字串，`server` 端接收到字串後，將其改成大寫並且送回給 `client` 端。 我們一開始將會透過 `UDP` 協定來實現這個任務。

`UDP` 是一種輕量化的協定，只會提供最低限度的服務，跟 `TCP` 相比，`UDP` 是**非連線導向**的協定，兩個 `process` 之間的溝通並不會事先握手，就像下圖所示，`UDP` 的 `client` 端只會接到指令之後送出，並不會在意對方是否有接收到資料，所以又被稱為 **不可靠的資料傳輸**。
在 `socket` 的 `api` 中，負責 `UDP` 傳送以及接收的 `function` 是 `sendto()`, `recvfrom()`。 因為 `UDP` 協定不需要事先連線，所以只需要有目標 `ip address` 跟 `port` 即可。

### sendto(int, const void *, size_t, int)

- [sendto(2) - Linux man page](https://linux.die.net/man/2/sendto)

```c
ssize_t sendto(int sockfd, const void *buf, size_t len, int flags,
               const struct sockaddr *dest_addr, socklen_t addrlen);
```

**sockfd**

`socket` 的文件描述符

**buf**

資料本體

**len**

資料長度

**flags**

一般填入 `0`，想知道詳細參數意義可以參考 [man page](https://linux.die.net/man/2/sendto)

**dest_addr**

目標位置相關資訊

**addrlen**

`dest_addr` 的 `size`

**return value**

傳送成功時回傳具體傳送成功的 `byte` 數，傳送失敗時會回傳 `-1`
並且把錯誤訊息存進 [errno](https://man7.org/linux/man-pages/man3/errno.3.html)

### recvfrom(int, void *, size_t, int)

- [recvfrom(2) - Linux man page](https://linux.die.net/man/2/recvfrom)

```c
ssize_t recvfrom(int sockfd, void *buf, size_t len, int flags,
                 struct sockaddr *src_addr, socklen_t *addrlen);
```

**sockfd**

`socket` 的文件描述符

**buf**

接收資料的 `buffer`

**len**

資料長度

**flags**

一般填入 `0`，想知道詳細參數意義可以參考 [man page](https://linux.die.net/man/2/recvfrom)

**src_addr**

資料來源地址，收到訊息之後我們可以一併收到來源地址，透過 `src_addr`，我們才能順利的把處理完的資料發回。

**addrlen**

`src_addr` 的 `size`

**return value**

接收成功時回傳具體接收成功的 `byte` 數，傳送失敗時會回傳 `-1`
並且把錯誤訊息存進 [errno](https://man7.org/linux/man-pages/man3/errno.3.html)

### example
***sever example***

```c
#define serverPort 48763

int main(int argc , char *argv[])
{
    // message buffer
    char buf[1024] = {0};

    // 建立 socket
    int socket_fd = socket(PF_INET , SOCK_DGRAM , 0);
    if (socket_fd < 0){
        printf("Fail to create a socket.");
    }
    
    // server 地址
    struct sockaddr_in serverAddr = {
        .sin_family = AF_INET,
        .sin_addr.s_addr = INADDR_ANY,
        .sin_port = htons(serverPort)
    };
    
    // 將建立的 socket 綁定到 serverAddr 指定的 port
    if (bind(socket_fd, (const struct sockaddr *)&serverAddr, sizeof(serverAddr)) < 0) {
        perror("Bind socket failed!");
        close(socket_fd);
        exit(0);
    }
    
    printf("Server ready!\n");

    struct sockaddr_in clientAddr;
    int len = sizeof(clientAddr);
    while (1) {
        // 當有人使用 UDP 協定送資料到 48763 port
        // 會觸發 recvfrom()，並且把來源資料寫入 clientAddr 當中
        if (recvfrom(socket_fd, buf, sizeof(buf), 0, (struct sockaddr *)&clientAddr, &len) < 0) {
            break;
        }

        // 收到 exit 指令就關閉 server
        if (strcmp(buf, "exit") == 0) {
            printf("get exit order, closing the server...\n");
            break;
        }
        
        // 將收到的英文字母換成大寫
        char *conv = convert(buf);

        // 顯示資料來源，原本資料，以及修改後的資料
        printf("get message from [%s:%d]: ", inet_ntoa(clientAddr.sin_addr), ntohs(clientAddr.sin_port));
        printf("%s -> %s\n", buf, conv);

        // 根據 clientAddr 的資訊，回傳至 client 端                
        sendto(socket_fd, conv, sizeof(conv), 0, (struct sockaddr *)&clientAddr, sizeof(clientAddr));

        // 清空 message buffer
        memset(buf, 0, sizeof(buf));
        free(conv);
    }
    // 關閉 socket，並檢查是否關閉成功
    if (close(socket_fd) < 0) {
        perror("close socket failed!");
    }
    
    return 0;
}
```

***client example***

```c
#define serverPort 48763
#define serverIP "127.0.0.1"

int main() 
{
    // message buffer
    char buf[1024] = {0};
    char recvbuf[1024] = {0};
    
    // 建立 socket
    int socket_fd = socket(PF_INET, SOCK_DGRAM, 0);
    if (socket_fd < 0) {
        printf("Create socket fail!\n");
        return -1;
    }

    // server 地址
    struct sockaddr_in serverAddr = {
        .sin_family = AF_INET,
        .sin_addr.s_addr = inet_addr(serverIP),
        .sin_port = htons(serverPort)
    };
    int len = sizeof(serverAddr);

    while (1) {
        // 輸入資料到 buffer
        printf("Please input your message: ");
        scanf("%s", buf);

        // 傳送到 server 端
        sendto(socket_fd, buf, sizeof(buf), 0, (struct sockaddr *)&serverAddr, sizeof(serverAddr));
        
        // 接收到 exit 指令就退出迴圈
        if (strcmp(buf, "exit") == 0) 
            break;

        // 清空 message buffer
        memset(buf, 0, sizeof(buf));

        // 等待 server 回傳轉成大寫的資料
        if (recvfrom(socket_fd, recvbuf, sizeof(recvbuf), 0, (struct sockaddr *)&serverAddr, &len) < 0) {
            printf("recvfrom data from %s:%d, failed!\n", inet_ntoa(serverAddr.sin_addr), ntohs(serverAddr.sin_port));
            break;
        }
        
        // 顯示 server 地址，以及收到的資料
        printf("get receive message from [%s:%d]: %s\n", inet_ntoa(serverAddr.sin_addr), ntohs(serverAddr.sin_port), recvbuf);
        memset(recvbuf, 0, sizeof(recvbuf));
    }
    // 關閉 socket，並檢查是否關閉成功
    if (close(socket_fd) < 0) {
        perror("close socket failed!");
    }

    return 0;
}
```

在 `/c_udp_socket` 下執行 `make` 即可。

![image](https://hackmd.io/_uploads/r1rJwCmYa.png)

![image](https://hackmd.io/_uploads/rJn-DAXtp.png)


***Note***
不知道各位有沒有注意到，我們正式使用 `socket` 的 `api` 時，關於位置的部份都是使用 `sockaddr` 當傳入的參數，我們在網路領域用的 `sockaddr_in` 在傳入時都要再強制轉型一次。

因為 `socket` 本身除了網路通訊之外有很多別的地方也會使用到，為了統一 `api` 操作，所以函式一律是用 `sockaddr` 作為參數，這樣一來各種不同的 `sockaddr_xx` 系列就可以用同一組 `api`，只需要額外轉型即可。

```c
recvfrom(socket_fd, recvbuf, sizeof(recvbuf), 0, (struct sockaddr *)&serverAddr, &len)
```

***想了解細節可以參考***[完整程式碼](https://github.com/bifanliu/socket_example/tree/main/c_udp_socket)

### reference
- [UDP Server-Client implementation in C](https://www.geeksforgeeks.org/udp-server-client-implementation-c/)

## C Socket TCP

接著我們要談談如何用 `socket` 利用 `TCP` 協定來交換資料，首先要知道的是 `TCP` 屬於 **連線導向`Connection-oriented`** 的協定，跟 `UDP` 不同，在雙方交換資料之前必須經過先建立 `TCP connection`，下方是 `socket` 利用 `TCP` 協定溝通的流程圖，可以跟之前提到 `UDP` 的流程圖做一個簡單的對比。

![](https://i.imgur.com/FDOIMj9.png)


先從 `server` 端來解說，跟 `UDP` 相比，可以看到 `bind` 完之後多了 `listen` 跟 `accept` 兩個動作。

當 `server` 端創立的 `socket` 成功 `bind` 某個 `port` 之後，他會開始 `listen` 有沒有人申請連線，在 `listen` 這個 `function` 還可以設定 `backlog`，這個參數可以決定今天我們的 `socket` 最多能同時處理的連線要求，避免同時太多人提出連線需求。

> *backlog*: 在 `server` 端 `accept` 之前最多的排隊數量



`TCP` 協定在建立連線時會經過 **three-way handshake** 流程，下圖是每個流程與 `socket api` 的對應圖。

![](https://i.imgur.com/IK8laxq.png)


當 `client` 呼叫 `connect` 時才會開始發起 **three-way handshake**，當 `connect` 結束時，`client` 與 `server` 基本已經完成了整個流程。

那 `server` 端的 `accept` 具體只是從 `server socket` 維護的 `completed connection queue` 中取出一個已完成交握過程的 `socket`。

在 `kernel` 中每個 `socket` 都會維護兩個不同的 `queue`:

- 未完成連線佇列 (***incomplete connection queue***): FIFO with syn_rcvd state
- 已完成連線佇列 (***complete connection queue***): FIFO with established state

> 所以 accept 根本不參與具體的 ***three-way handshake*** 流程


**總結一下**

- `server` 端
    - `listen`: 初始化佇列，準備接受 `connect`
    - `accept`: 從 `complete connection queue` 中取出一個已連線的 `socket`
- `client` 端
    - `connect`: 發起 `three-way handshake`，必須要等 `server` 端開始 `listen` 後才可以使用

### connect(int, const struct sockaddr *, socklen_t )

- [connect(2) Linux man page](https://man7.org/linux/man-pages/man2/connect.2.html)

```c
int connect(int sockfd, const struct sockaddr *addr,
            socklen_t addrlen);
```

**sockfd** 

一開始呼叫 `socket()` 的回傳值

**addr**

想要建立連線的 `server` 資料

**addrlen**

`addr` 結構的 `size`

**return**

錯誤時回傳 `-1`，並且設定 `errno`

### listen(int, int )

- [listen(2) - Linux man page](https://man7.org/linux/man-pages/man2/listen.2.html)

```c
int listen(int sockfd, int backlog);
```

**sockfd**

一開始呼叫 `socket()` 的回傳值

**backlog**

允許進入 `queue` 的最大連線數量

在 `server` 端還沒有 `accept` 之前，最多能允許幾個 `socket` 申請 `connect`

> 詳細敘述可以參考 [man page](https://man7.org/linux/man-pages/man2/listen.2.html)

**return**

錯誤時回傳 `-1`，並且設定 `errno`

### accept(int, struct sockaddr *, socklen_t * )

- [accept(2) Linux man page](https://man7.org/linux/man-pages/man2/accept.2.html)

```c
int accept(int sockfd, struct sockaddr *addr,socklen_t *addrlen);
```

**sockfd**

`server` 端 `socket` 的檔案描述符

**addr**

建立 `TCP` 連線的 `Client` 端資料

**addrlen**

`addr` 結構的 `size`

**return**

返回一個新的 `sock_fd`，專門跟請求連結的 `client` 互動

### example

![](https://i.imgur.com/T35C7vs.png)

***server example***

```c
#define serverPort 48763

// message buffer
char buf[1024] = {0};

// 建立 socket
int socket_fd = socket(PF_INET , SOCK_STREAM , 0);
if (socket_fd < 0){
    printf("Fail to create a socket.");
}

// server 地址
struct sockaddr_in serverAddr = {
    .sin_family = AF_INET,
    .sin_addr.s_addr = INADDR_ANY,
    .sin_port = htons(serverPort)
};

// 將建立的 socket 綁定到 serverAddr 指定的 port
if (bind(socket_fd, (const struct sockaddr *)&serverAddr, sizeof(serverAddr)) < 0) {
    perror("Bind socket failed!");
    close(socket_fd);
    exit(0);

// 初始化，準備接受 connect
// backlog = 5，在 server accept 動作之前，最多允許五筆連線申請
// 回傳 -1 代表 listen 發生錯誤
if (listen(socket_fd, 5) == -1) {
    printf("socket %d listen failed!\n", socket_fd);
    close(socket_fd);
    exit(0);
}

printf("server [%s:%d] --- ready\n", 
        inet_ntoa(serverAddr.sin_addr), ntohs(serverAddr.sin_port));

while(1) {
    int reply_sockfd;
    struct sockaddr_in clientAddr;
    int client_len = sizeof(clientAddr);

    // 從 complete connection queue 中取出已連線的 socket
    // 之後用 reply_sockfd 與 client 溝通
    reply_sockfd = accept(socket_fd, (struct sockaddr *)&clientAddr, &client_len);
    printf("Accept connect request from [%s:%d]\n", 
            inet_ntoa(clientAddr.sin_addr), ntohs(clientAddr.sin_port));
    
    // 不斷接收 client 資料
    while (recv(reply_sockfd, buf, sizeof(buf), 0)) {
        // 收到 exit 指令就離開迴圈
        if (strcmp(buf, "exit") == 0) {
            memset(buf, 0, sizeof(buf));
            goto exit;
        }

        // 將收到的英文字母換成大寫
        char *conv = convert(buf);

        // 顯示資料來源，原本資料，以及修改後的資料
        printf("get message from [%s:%d]: ",
                inet_ntoa(clientAddr.sin_addr), ntohs(clientAddr.sin_port));
        printf("%s -> %s\n", buf, conv);

        // 傳回 client 端
        // 不需要填入 client 端的位置資訊，因為已經建立 TCP 連線
        if (send(reply_sockfd, conv, sizeof(conv), 0) < 0) {
            printf("send data to %s:%d, failed!\n", 
                    inet_ntoa(clientAddr.sin_addr), ntohs(clientAddr.sin_port));
            memset(buf, 0, sizeof(buf));
            free(conv);
            goto exit;
        }

        // 清空 message buffer
        memset(buf, 0, sizeof(buf));
        free(conv);
    }

    // 關閉 reply socket，並檢查是否關閉成功
    if (close(reply_sockfd) < 0) {
        perror("close socket failed!");
    }
}
```

***client example***

```c
#define serverPort 48763

 // message buffer
char buf[1024] = {0};
char recvbuf[1024] = {0};

// 建立 socket
int socket_fd = socket(PF_INET, SOCK_STREAM, 0);
if (socket_fd < 0) {
    printf("Create socket fail!\n");
    return -1;
}

// server 地址
struct sockaddr_in serverAddr = {
    .sin_family = AF_INET,
    .sin_addr.s_addr = inet_addr(serverIP),
    .sin_port = htons(serverPort)
};
int len = sizeof(serverAddr);

// 試圖連結 server，發起 tcp 連線
// 回傳 -1 代表 server 可能還沒有開始 listen
if (connect(socket_fd, (struct sockaddr *)&serverAddr, len) == -1) {
    printf("Connect server failed!\n");
    close(socket_fd);
    exit(0);
}

printf("Connect server [%s:%d] success\n",
            inet_ntoa(serverAddr.sin_addr), ntohs(serverAddr.sin_port));

while (1) {
    // 輸入資料到 buffer
    printf("Please input your message: ");
        if (fgets(buf, sizeof(buf), stdin) == NULL) {
            printf("Error reading input\n");
            break;
        }

    // 傳送到 server 端
    if (send(socket_fd, buf, sizeof(buf), 0) < 0) {
        printf("send data to %s:%d, failed!\n", 
                inet_ntoa(serverAddr.sin_addr), ntohs(serverAddr.sin_port));
        memset(buf, 0, sizeof(buf));
        break;
    }

    // 接收到 exit 指令就退出迴圈
    if (strcmp(buf, "exit") == 0)
        break;

    // 清空 message buffer
    memset(buf, 0, sizeof(buf));

    // 等待 server 回傳轉成大寫的資料
    if (recv(socket_fd, recvbuf, sizeof(recvbuf), 0) < 0) {
        printf("recv data from %s:%d, failed!\n", 
                inet_ntoa(serverAddr.sin_addr), ntohs(serverAddr.sin_port));
        break;
    }

    // 顯示 server 地址，以及收到的資料
    printf("get receive message from [%s:%d]: %s\n", 
            inet_ntoa(serverAddr.sin_addr), ntohs(serverAddr.sin_port), recvbuf);
    memset(recvbuf, 0, sizeof(recvbuf));
}

// 關閉 socket，並檢查是否關閉成功
if (close(socket_fd) < 0) {
    perror("close socket failed!");
}
```
![image](https://hackmd.io/_uploads/rkne_xNta.png)

使用

```bash
netstat -a | grep 48763
```

查看是否建立連線

![image](https://hackmd.io/_uploads/Bkjmdg4Y6.png)

***想了解細節可以參考***[完整程式碼](https://github.com/bifanliu/socket_example/tree/main/c_tcp_socket)

### reference
- [TCP Socket Programming 學習筆記](http://zake7749.github.io/2015/03/17/SocketProgramming/)
- [地址轉換函數 inet_addr(), inet_aton(), inet_ntoa()和inet_ntop(), inet_pton()](http://haoyuanliu.github.io/2017/01/15/%E5%9C%B0%E5%9D%80%E8%BD%AC%E6%8D%A2%E5%87%BD%E6%95%B0inet-addr-inet-aton-inet-ntoa-%E5%92%8Cinet-ntop-inet-pton/)
- [Beej's guide to networking programming](https://beej-zhtw-gitbook.netdpi.net/dao_du)
- [socket listen() 分析](https://www.cnblogs.com/codestack/p/11099565.html)
- [從 Linux 原始碼看 socket accept](https://www.readfog.com/a/1638167776017354752)

## Python Socket Function Introduction

Python 提供了兩個基本的socket 模組：

* `Socket` 它提供了標準的BSD Socket API。
* `SocketServer` 它提供了伺服器重心，可以簡化網頁伺服器的開發。

下面講解下Socket模組功能。
 
### Socket 類型
套接字格式：socket(family, type[,protocal]) 使用給定的套接族，套接字類型，協定編號（預設為0）來建立套接字

socket 類型| 描述
:--- | :---
socket.AF_UNIX | 用於同一台機器上的進程通訊（既本機通訊）
socket.AF_INET | 用於伺服器與伺服器之間的網路通訊
socket.AF_INET6 | 基於IPV6方式的伺服器與伺服器之間的網路通訊
socket.SOCK_STREAM | 基於TCP的流式socket通訊
socket.SOCK_DGRAM | 基於UDP的資料報式socket通訊
socket.SOCK_RAW | 原始套接字，普通的套接字無法處理ICMP、IGMP等網路報文，而SOCK_RAW可以；其次SOCK_RAW也可以處理特殊的IPV4報文；此外，利用原始套接字，可以透過IP_HDRINCL套接字選項由使用者建構IP頭
socket.SOCK_SEQPACKET | 可靠的連續資料包服務

建立TCP Socket：
``` Python
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
```

建立UDP Socket：
``` Python
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
```

### Socket 函數
* TCP發送資料時，已建立好TCP鏈接，所以不需要指定地址，而UDP是面向無連接的，每次發送都需要指定發送給誰。
* 伺服器與客戶端不能直接發送列表，元素，字典等帶有資料類型的格式，發送的內容必須是字串資料。

**伺服器端Socket 函數**

Socket 函數| 描述
:--- | :---
s.bind(address) | 將套接字綁定到位址，在AF_INET下，以tuple(host, port)的方式傳入，如s.bind((host, port))
s.listen(backlog) | 開始監聽TCP傳入連接，backlog指定在拒絕連結前，作業系統可以掛起的最大連接數，該值最少為1，大部分應用程式設為5就夠用了
s.accept() | 接受TCP連結並返回（conn, address），其中conn是新的套接字對象，可以用來接收和發送數據，address是連結客戶端的地址。

**客戶端Socket 函數**

Socket 函數| 描述
:--- | :---
s.connect(address) | 連結到address處的套接字，一般address的格式為tuple(host, port)，如果連結出錯，則回傳socket.error錯誤
s.connect_ex(address) | 功能與s.connect(address)相同，但成功回傳0，失敗回傳errno的值

**公共Socket 函數**

Socket 函數| 描述
:--- | :---
s.recv(bufsize[, flag]) | 接受TCP套接字的數據，數據以字符串形式返回，buffsize指定要接受的最大數據量，flag提供有關消息的其他信息，通常可以忽略
s.send(string[, flag]) | 發送TCP數據，將字串中的資料傳送到連結的套接字，傳回值是要傳送的位元組數量，該數量可能小於string的位元組大小
s.sendall(string[, flag]) | 完整發送TCP數據，將字串中的數據發送到連結的套接字，但在返回之前嘗試發送所有數據。成功回傳None，失敗則拋出例外
s.recvfrom(bufsize[, flag]) | 接受UDP套接字的資料u，與recv()類似，但傳回值是tuple(data, address)。其中data是包含接受資料的字串，address是發送資料的套接字位址
s.sendto(string[, flag], address) | 傳送UDP數據，將資料傳送至套接字，address形式為tuple(ipaddr, port)，指定遠端位址傳送，傳回值是傳送的位元組數
s.close() | 關閉套接字
s.getpeername() | 傳回套接字的遠端位址，傳回值通常是一個tuple(ipaddr, port)
s.getsockname() | 傳回套接字自己的位址，回傳值通常是一個tuple(ipaddr, port)
s.setsockopt(level, optname, value) | 設定給定套接字選項的值
s.getsockopt(level, optname[, buflen]) | 傳回套接字選項的值
s.settimeout(timeout) | 設定套接字操作的逾時時間，timeout是一個浮點數，單位是秒，值為None則表示永遠不會逾時。一般超時期應在剛創建套接字時設置，因為他們可能用於連接的操作，如s.connect()
s.gettimeout() | 傳回目前逾時值，單位是秒，如果沒有設定超時則回傳None
s.fileno() | 傳回套接字的檔案描述
s.setblocking(flag) | 如果flag為0，則將套接字設為非阻塞模式，否則將套接字設定為阻塞模式（預設值）。非阻塞模式下，如果呼叫recv()沒有發現任何數據，或send()呼叫無法立即傳送數據，那麼將會造成socket.error異常。
s.makefile() | 建立一個與該套接字相關的文件

### Socket 程式設計思想

**TCP 伺服器**
1.建立套接字，綁定套接字到本地IP與端口
``` Python
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind()
```

2、開始監聽連結
``` Python
s.listen()
```

3.進入循環，不斷接受客戶端的連結請求
``` Python
While True:
    s.accept()
```

4.接收客戶端傳來的數據，並且發送給對方發送數據
``` Python
s.recv()
s.sendall()
```

5.傳輸完畢後，關閉套接字
``` Python
s.close()
```

**TCP 客戶端**
1、建立套接字並連結至遠端位址
``` Python
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect()
```

2、連​​結後發送數據及接收數據
``` Python
s.sendall()
s.recv()
```

3.傳輸完畢後，關閉套接字

### reference
- [python socket](https://ithelp.ithome.com.tw/articles/10205819)
- [Python Socket 網路通訊教學](https://shengyu7697.github.io/python-socket/#google_vignette)
- [Python 多執行緒 threading 模組平行化程式設計教學
2018/05/17](https://blog.gtwang.org/programming/python-threading-multithreaded-programming-tutorial/)

## Python TCP example
***Server example***

這邊介紹 Python Socket TCP 伺服器端與客戶端的網路通訊程式，TCP 這種連線協議具有可靠性，因為 TCP 協議有重傳的機制，所以收到的封包一定沒有錯誤，也因為 TCP 協議的關係在傳輸速度上會有所犧牲，在稍後會介紹 UDP 無重傳機制，提升傳輸性能，不過 TCP 還是給我們帶來很大的便利性，一般瀏覽網頁的 HTTP 協議就是基於 TCP 的基礎，接下來示範一下簡單的 Python Socket TCP Server 伺服器端程式，

如下例所示，伺服器端一開始建立 socket，socket.AF_INET 表示使用 Internet Protocol 的通訊協定，而 socket.SOCK_STREAM 表示傳輸方式為 TCP，用 bind() 綁定，這裡是使用 0.0.0.0, port 為 7000，

使用 listen() 開始監聽，上限連線數為5，之後進入主迴圈，accept() 等待接受客戶端的連線請求，一旦有客戶端連線的話，就會從 accept() 繼續往下執行，

接著從這個連線就會進入thread， recv() 接收資料與 send() 傳送資料，主程式則是會回到 accept() 等待新的客戶端連線，等到新的客戶端連線連上便跟之前的流程一樣，這樣便是一個完整的 Python Socket TCP 伺服器程式。
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
HOST = '0.0.0.0'
PORT = 7000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(5)

print('server start at: %s:%s' % (HOST, PORT))
print('wait for connection...')

while True:
    conn, addr = s.accept()
    t = threading.Thread(target=job, args=(conn,))
    t.start()

s.close()
```

***client example***

如下例所示，客戶端一開始建立 socket，之後 connect() 連線伺服器主機的 host 與 port，
接著使用 send() 把字串發送給伺服器端，然後使用 recv() 接收來至伺服器端的資料，接收到資料後就把它印出來，重複循環直到client端打出exit才會結束
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
HOST = '0.0.0.0'
PORT = 7000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

while True:
    # read user input
    user_input = input("Please input yout messae: ")

    print(user_input)

    # send to server
    s.send(user_input.encode("utf-8"))

    # if string is exit then over
    if user_input.lower() == "exit":
        break

    # server writeback data
    indata = s.recv(1024)

    # decode
    indata_decode = indata.decode()

    # print writeback data
    print("Write Back Message content is " + indata_decode)

print("client is over")

s.close()
```

***execute step***
```
python3 server.py
python3 client.py
python3 client.py
```

***result***
![image](https://hackmd.io/_uploads/SyFMwWVYp.png)

***想了解細節可以參考***[完整程式碼](https://github.com/bifanliu/socket_example/tree/main/py_tcp_socket)


## Python UDP example

這邊介紹 Python Socket UDP 服器端與客戶端的網路通訊程式，UDP 無重傳機制，所以相對於 TCP 來說是傳輸效率較好，但因為不保證資料正確性的關係，意味著必須自己實作資料檢查機制，接下來示範一下簡單的 Python Socket UDP Server 伺服器端程式，

如下例所示，伺服器端一開始建立 socket，socket.AF_INET 表示使用 Internet Protocol 的通訊協定，而 socket.SOCK_DGRAM 表示傳輸方式為 UDP，用 bind() 綁定，這裡是使用 0.0.0.0, port 為 7000，

跟 TCP 不同的是 UDP 不需使用 listen() 與 accept()，直接使用 recvfrom 來接收任何一個 socket 地址的客戶端資料，以及 sendto 傳送資料給指定 socket 位址的客戶端，這邊用一個迴圈不斷地重複 recvfrom() 接收資料與 sendto() 傳送資料，值到任意一個client端打出exit，這樣便是一個完整的 Python Socket UDP 伺服器程式。

***server example***

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
HOST = '0.0.0.0'
PORT = 7000

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST, PORT))

print('server start at: %s:%s' % (HOST, PORT))
print('wait for connection...')

while True:
    # receive data
    indata, addr = s.recvfrom(1024)

    # decode
    indata_decode = indata.decode()

    # if input data content doesn't exit then keep loop
    if indata_decode.lower() == "exit":
        break

    # print write back client content
    upperstring = indata_decode.upper()
    print("Server Message is " + upperstring)

    # write back to client
    s.sendto(upperstring.encode("utf-8"), addr)

s.close()
```
***UDP client example***

下面範例是對應的 Python Socket UDP Client 端的code，如下例所示，client端一開始建立 socket，跟 TCP 不同的是 UDP 不需要 connect() 而是直接用 sendto() 將資料送往指定的主機 host 與 port，
接著使用 sendto() 把字串發送給伺服器端，然後使用 recvfrom() 接收來至伺服器端的資料，接收到資料後就把它印出來，重複循環直到client端打出exit才會結束，

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
HOST = '0.0.0.0'
PORT = 7000

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect((HOST, PORT))

while True:
    # read user input
    user_input = input("Please input yout messae: ")

    print(user_input)

    # send to server
    s.sendto(user_input.encode("utf-8"), (HOST, PORT))

    # if string is exit then over
    if user_input.lower() == "exit":
        break

    # server writeback data
    indata, addr = s.recvfrom(1024)

    # decode
    indata_decode = indata.decode("utf-8")

    # print writeback data
    print("Write Back Message content is " + indata_decode)

print("client is over")

s.close()
```

***excute step***
```
python3 server.py
python3 client.py
```

***result***
![image](https://hackmd.io/_uploads/rJdX0WEt6.png)

***想了解細節可以參考***[完整程式碼](https://github.com/bifanliu/socket_example/tree/main/py_udp_socket)