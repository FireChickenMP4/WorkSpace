package main

import "fmt"

func main() {
	s := make([]byte, 5)
	fmt.Println(len(s), cap(s)) // 5 5
	s = s[2:4]
	fmt.Println(len(s), cap(s)) // 2 3 因为2:4不包括4，经典end不是最后一个
	//但是这里3其实是从2切到最后，所以cap是3
	//cap切片=底层数组长度 - 切片起始索引
	//验证：
	s = s[2:3]
	// ???不懂，之后再说，好像切片再切不大一样
	fmt.Println(len(s), cap(s))
	str := "hello，世界"
	for i := range str {
		fmt.Println(i, str[i])
	}
	fmt.Println(len(str))
	//这里的话应该想说的是ascii码的事情，中文符号和字都不是
	//只占用一个字节，所以读取次数和长度并不一样，并且跳着蹦着的
	//01234是前五个英文字母
	//5到7是中文逗号
	//8到10 11到13分别是世界
}
