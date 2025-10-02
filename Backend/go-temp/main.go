package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/http/cookiejar"
	"net/url"
	"os"
	"strings"
)

// client与jar,还有拟游览器UA
var (
	jar    *cookiejar.Jar
	client *http.Client
)

const (
	ua string = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.54"
)

type LoginResponse struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
	Data    struct {
		Cookie []string `json:"cookie"`
	} `json:"data"`
}
type RoomidsResponse struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
	Data    struct {
		Roomids []string `json:"room_ids"`
	} `json:"data"`
}
type QueryUser struct {
	Name   string   `json:"name"`
	Roomid []string `json:"room_ids"`
}
type QueryResponse struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
	Data    struct {
		Seat     string `json:"seat"`
		Ilibrary bool   `json:"is_in_library"`
		Area     string `json:"area"`
		Start    string `json:"start"`
		End      string `json:"end"`
	} `json:"data"`
}
type SeatResponse struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
	Data    struct {
		Seatinfo []struct {
			Seat        string `json:"seat"`
			Is_occupied bool   `json:"is_occupied"`
			Owner       string `json:"owner"`
			Start       string `json:"start"`
			End         string `json:"end"`
		} `json:"seat_infos"`
	} `json:"data"`
}

func erf(err error) {
	if err != nil {
		fmt.Println(err)
		return
	}
}

func my_freopen() (string, string) {
	usn, err := os.ReadFile("usn.txt")
	erf(err)
	psw, err := os.ReadFile("psw.txt")
	erf(err)
	return string(usn), string(psw)
}

func login(usn, psw string) {
	const purl string = "https://demo.muxixyz.com/library/login"
	//请求体设置
	postData, err := json.Marshal(map[string]string{
		"username": usn,
		"password": psw,
	})
	erf(err)

	//post请求，login
	postReq, err := http.NewRequest("POST", purl, bytes.NewBuffer(postData))
	erf(err)
	//请求头
	postReq.Header.Set("Content-Type", "application/json")
	postReq.Header.Set("User-Agent", ua)
	resp, err := client.Do(postReq)
	erf(err)
	defer resp.Body.Close()
	body, err := io.ReadAll(resp.Body)
	erf(err)

	//提取cookie
	var body_p LoginResponse
	err = json.Unmarshal(body, &body_p)
	erf(err)

	//将cookie手动加到cookiejar中
	targetUrl, err := url.Parse("https://demo.muxixyz.com")
	if err != nil {
		fmt.Println(err)
		return
	}
	erf(err)
	cookie := strings.Split(body_p.Data.Cookie[0], "=")
	jar.SetCookies(targetUrl, []*http.Cookie{
		{
			Name:  cookie[0],
			Value: cookie[1],
			Path:  "/",
		},
	})
}

func getrid() []string {
	const purl string = "https://demo.muxixyz.com/library/roomids"
	//get请求，get roomids
	getReq, err := http.NewRequest("GET", purl, nil)
	erf(err)
	getReq.Header.Set("Content-Type", "application/json")
	getReq.Header.Set("User-Agent", ua)
	resp, err := client.Do(getReq)
	erf(err)
	defer resp.Body.Close()
	//处理get返回的json数据

	body, err := io.ReadAll(resp.Body)
	erf(err)
	var body_g RoomidsResponse
	err = json.Unmarshal(body, &body_g)
	erf(err)
	//输出roomids
	fmt.Println("查询到可用的房间号如下:", body_g.Data.Roomids)
	return body_g.Data.Roomids
}

func queryseat(roomid []string) bool {
	const purl string = "https://demo.muxixyz.com/library/seatinfo"
	fmt.Println("以下是可查询的所有房间已用座位信息:")
	ans_1 := 0
	for id, rd := range roomid {
		var rid []string = roomid[id : id+1]
		postData, err := json.Marshal(map[string][]string{
			"room_ids": rid,
		})
		erf(err)
		postReq, err := http.NewRequest("POST", purl, bytes.NewBuffer(postData))
		erf(err)
		postReq.Header.Set("Content-Type", "application/json")
		postReq.Header.Set("User-Agent", ua)
		resp, err := client.Do(postReq)
		erf(err)
		defer resp.Body.Close()

		//处理post返回的json数据
		var body_p SeatResponse
		body, _ := io.ReadAll(resp.Body)
		err = json.Unmarshal(body, &body_p)
		erf(err)
		ans := 0
		var freeSeat []string
		for _, value := range body_p.Data.Seatinfo {
			if value.Is_occupied {
				fmt.Println("房间号:", rd, " 座位：", value.Seat, " 使用者:", value.Owner, " 时间:", value.Start, "-", value.End)
				ans++
			} else {
				freeSeat = append(freeSeat, value.Seat)
			}
		}
		if ans == 0 {
			fmt.Println("座位均空,无人使用,座位号为:", freeSeat)
		} else {
			fmt.Println("而房间", rd, "有这些座位为空:", freeSeat)
			ans_1++
		}
	}
	if ans_1 == 0 {
		fmt.Println("所有房间均空，怎么可能？？？哦，我的上帝，你是不是忘了这个点可能闭馆了？？？")
		return false
	}
	return true
}

func queryuser(roomid []string) {
	const purl string = "https://demo.muxixyz.com/library/inlibrary"
	//先处理查询用户是否在馆的postdata
	var name string
	fmt.Println("请输入要查询的姓名:")
	fmt.Scan(&name)
	query := QueryUser{
		Name:   name,
		Roomid: roomid,
	}
	postData, err := json.Marshal(query)
	erf(err)
	postReq, err := http.NewRequest("POST", purl, bytes.NewBuffer(postData))
	erf(err)
	postReq.Header.Set("Content-Type", "application/json")
	postReq.Header.Set("User-Agent", ua)
	resp, err := client.Do(postReq)
	erf(err)
	defer resp.Body.Close()
	body_p1, err := io.ReadAll(resp.Body)
	erf(err)

	//处理返回体
	var body_q QueryResponse
	err = json.Unmarshal(body_p1, &body_q)
	if err != nil {
		fmt.Println(err)
		return
	}
	fmt.Print("查询结果:", body_q.Message)
	fmt.Println()
}

func my_read(kb string) bool {
	if kb == "n" || kb == "N" || kb == "no" || kb == "No" || kb == "nO" || kb == "NO" || kb == "n0" || kb == "N0" {
		return false
	} else {
		return true
	}
}

func main() {
	fmt.Println("请输入用户名和密码:")
	//	var usn, psw string
	//	fmt.Scan(&usn, &psw)
	//	这里暂时使用文本输入账密，懒得去做freopen效果了，就直接单个变量赋值得了
	usn, psw := my_freopen()

	//cookiejar管理cookie,并创建客户端
	var err error
	jar, err = cookiejar.New(nil)
	erf(err)
	client = &http.Client{
		Jar: jar,
	}

	login(usn, psw)
	roomid := getrid()
	var isfree, yn bool = true, true
	fmt.Println("请问是否要查看所有房间的座位情况:(y/n)(默认值为y)")
	var kb string = ""
	fmt.Scan(&kb)
	yn = my_read(kb)

	if yn {
		isfree = queryseat(roomid)
	}
	if isfree {
		queryuser(roomid)
		return
	} else {
		fmt.Scan()
		fmt.Println("这里是空的QAQ，不要再试图视奸别人了哦awa")
		return
	}
}
