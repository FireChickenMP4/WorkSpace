\*\*# MarkDown 语法

#### 前言：Markdown 是一种轻量级标记语言，排版语法简洁，让人们更多地关注内容本身而非排版。它使用易读易写的纯文本格式编写文档，可与 HTML 混编，可导出 HTML、PDF 以及本身的 .md 格式的文件。因简洁、高效、易读、易写，Markdown 被大量使用，如 Github、Wikipedia、简书等。

## 一.Markdown 标题语法

# Head1

## Head2

### Head3

#### Head4

##### Head5

###### Head6

####### Head7 //不存在

//分别对应 1 到 6 个井号，井号后面要加空格，不同的 Markdown 应用程序处理 `#` 和标题之间的空格方式并不一致。为了兼容考虑，请用一个空格在 `#` 和标题之间进行分隔。

当然还有可选语法，但是 typora 不兼容第一个好像？html 还是可以插入的

<h1>你好</h1>

![image-20251029154258076](C:\Users\1\AppData\Roaming\Typora\typora-user-images\image-20251029154258076.png)

## 二.Markdown 段落

要创建段落，请使用空白行将一行或多行文本进行分隔。(为什么不能直接就来个回车？)

I really like using Markdown.

I think I'll use it to format all of my documents from now on.

html 的用 \<p\> \</p\>

<p>I really like using Markdown.</p>

<p>I think I'll use it to format all of my documents from now on.</p>

不要用空格（spaces）或制表符（ tabs）缩进段落。

## 三.Markdown 换行语法

在一行的末尾添加两个或多个空格，然后按回车键,即可创建一个换行(`<br>`)。

\<p\> \<br\> \</p\>

<p> This is the first line.  <br>
    And this is the second line.
</p>

### 换行（Line Break）用法的最佳实践

几乎每个 Markdown 应用程序都支持两个或多个空格进行换行，称为 `结尾空格（trailing whitespace)` 的方式，但这是有争议的，因为很难在编辑器中直接看到空格，并且很多人在每个句子后面都会有意或无意地添加两个空格。由于这个原因，你可能要使用除结尾空格以外的其它方式来换行。幸运的是，几乎每个 Markdown 应用程序都支持另一种换行方式：HTML 的 `<br>` 标签。

为了兼容性，请在行尾添加“结尾空格”或 HTML 的 `<br>` 标签来实现换行。

还有两种其他方式我并不推荐使用。CommonMark 和其它几种轻量级标记语言支持在行尾添加反斜杠 (`\`) 的方式实现换行，但是并非所有 Markdown 应用程序都支持此种方式，因此从兼容性的角度来看，不推荐使用。并且至少有两种轻量级标记语言支持无须在行尾添加任何内容，只须键入回车键（`return`）即可实现换行。

## 三.Markdown 强调语法

#### 1.粗体

html 就是 strong 开头/strong 结尾

Markdown 里面是\*\*is\*\* \_\_is\_\_好像也行

This is **bold**.

And this is **bold**too

#### 2.斜体

html em /em

\*is\* 或者 \_is\_ //但是 typora 不支持后面这个

*aaaa*www*aaaa*

这俩尽量都有星号，兼容性考虑

#### 3.斜粗体

html 直接套一块就行

md 也是，其实就是三个星号

## 四.Markdown 引用语法

要创建块引用，请在段落前加一个>符号

> 引用喵 引用喵~

//typora 好像在引用里面换行是自动续上的，但是在空行连续两个回车就会推出去

#### 多个段落的块引用

块引用可以包含多个段落。为段落之间的空白行添加一个 `>`符号。

\>qqq

\>

\>qqq

然后渲染出来是两个段落的引用，但是 ty 不是这样的

然后这个引用可以嵌套，`>>`就可以

> 引用喵
>
> 引用喵喵喵
>
> > 引用喵喵喵
> >
> > > 三层喵

块引用可以包含其他 Markdown 格式的元素。并非所有元素都可以使用，你需要进行实验以查看哪些元素有效。

## 五.Markdown 列表语法

可以将多个条目组织成有序或无序列表。

#### 1.有序列表

要创建有序列表，请在每个列表项前添加数字并紧跟一个英文句点。数字不必按数学顺序排列，但是列表应当以数字 1 起始。

1. awa

2. 222

3. 333

4. qwq

5. 第五人格启动

   d

6. eee //会发现你就算在有序列表里把号删掉，但还是有这种左对齐的感觉

   //需要空白行连敲回车才行

回来了 html 的话就是 ol li li li li.... /ol

当然可以嵌套

#### 2. 无序列表

`-*+`都可以

- awa
-

* awa

//然后你发现两个不同列表还是有区别的，间隔上

当然可以嵌套

//会发现你就算在有序列表里把号删掉，但还是有这种左对齐的感觉

这个其实是嵌套段落了算是（

## 六.Markdown 代码语法

短的 \` \` 之中 就可以 `qwq`

\可以转义

代码块的话，请将代码块的每一行缩进至少四个空格或一个制表符。

//ty 好像 不行

但是拓展语法里面有围栏 代码块 ，这个可以

用三个`就可以，类似 py 的多行字符串一样

```desuwa
代码跌丝袜
```

当然特定语言是可以语法高亮的，在头起的三个后跟代码语言

```json
{
  "firstName": "John",
  "lastName": "Smith",
  "age": 25
}
```

## 六.Markdown 分割线语法

单独一样三个`*-_`

---

ty 三个都可以

为了最好的效果，最好分割线上下有空行

## 七.Markdown 链接语法

html 的话

```html
<a href="地址" title="title名字">显示名</a>
```

md 的话是`[显示名](链接 "悬浮链接显示名")`

<a href="https://www.bilibili.com/video/BV1vUGbzxEQH">[剧场版]假如睦第二人格是爱音</a>

[颂乐人偶](https://www.bilibili.com/bangumi/play/ep1231523 "Ave mujica")

其实 ty 里直接粘贴格式就是 md 格式

使用尖括号可以很方便地把 URL 或者 email 地址变成可点击的链接。

<https://www.bilibili.com/video/BV1uHASeXEMM>

<1111@163.com>

带格式化的链接

[强调](https://markdown.com.cn/basic-syntax/headings.html#emphasis) 链接, 在链接语法前后增加星号。 要将链接表示为代码，请在方括号中添加反引号。

```text
I love supporting the **[EFF](https://eff.org)**.
This is the *[Markdown Guide](https://www.markdownguide.org)*.
See the section on [`code`](#code).
```

I love supporting the **[EFF](https://eff.org)**.
This is the _[Markdown Guide](https://www.markdownguide.org)_.
See the section on [`code`](#code).

#### 引用类型链接

引用样式链接是一种特殊的链接，它使 URL 在 Markdown 中更易于显示和阅读。参考样式链接分为两部分：与文本保持内联的部分以及存储在文件中其他位置的部分，以使文本易于阅读。

链接的第一部分格式

引用类型的链接的第一部分使用两组括号进行格式设置。第一组方括号包围应显示为链接的文本。第二组括号显示了一个标签，该标签用于指向您存储在文档其他位置的链接。

尽管不是必需的，可以在第一组和第二组括号之间包含一个空格。第二组括号中的标签不区分大小写，可以包含字母，数字，空格或标点符号。

```
[【安科xMyGO】如果说crychic和平解散的话#0][1]
[丰川祥子获得了【亏钱系统】#1 亏得越多，赚得越多？！] [2]
```

[【安科 xMyGO】如果说 crychic 和平解散的话#0][1]

[丰川祥子获得了【亏钱系统】#1 亏得越多，赚得越多？！] [2]

//这种，ty 好像不支持第二种

[丰川祥子获得了【亏钱系统】#1 亏得越多，赚得越多？！][2]

链接的第二部分格式

引用类型链接的第二部分使用以下属性设置格式：

1. 放在括号中的标签，其后紧跟一个冒号和至少一个空格（例如`[label]:`）。
2. 链接的 URL，可以选择将其括在尖括号中。
3. 链接的可选标题，可以将其括在双引号，单引号或括号中。

以下示例格式对于链接的第二部分效果相同：

```
[1]: https://www.bilibili.com/video/BV1vtxYzYE4X/
[2]: https://www.bilibili.com/video/BV1DZ421M7Uh
```

[1]: https://www.bilibili.com/video/BV1vtxYzYE4X/ "【安科xMyGO】如果说crychic和平解散的话#0"
[2]: https://www.bilibili.com/video/BV1DZ421M7Uh "丰川祥子获得了【亏钱系统】#1 亏得越多，赚得越多？！"

不同的 Markdown 应用程序处理 URL 中间的空格方式不一样。为了兼容性，请尽量使用%20 代替空格。

## 八.Markdown 图片语法

html 的话

```html
<img src="图片源" alt="加载失败替换图片" tilte="“图片title”" />
```

md 是

```
![这是图片](图片源 "title")
```

![125576974_p0](E:\1\1\pictures\125576974_p0.png "这是兔兔，她很可爱")

虽然 ty 也会自动处理粘贴的图片就是了

#### 链接图片

```text
[![沙漠中的岩石图片](/assets/img/shiprock.jpg "Shiprock")](https://markdown.com.cn)
```

这样就可以超链接了

[![【MyGO】素世的MyGO二周目，但是角色对调](.\bilibili_BV16G8meNENx_IMG.jpg)](https://www.bilibili.com/video/BV16G8meNENx/ "超链接图片")

看来 ty 并不行（

## 九.Markdown 转义字符语法

要显示原本用于格式化 Markdown 文档的字符，请在字符前面添加反斜杠字符 \ 。

\* aaaa

#### 特殊字符自动转义

在 HTML 文件中，有两个字符需要特殊处理： `<` 和 `&` 。 `<` 符号用于起始标签，`&` 符号则用于标记 HTML 实体，如果你只是想要使用这些符号，你必须要使用实体的形式，像是 `<` 和 `&`。

`&` 符号其实很容易让写作网页文件的人感到困扰，如果你要打「AT&T」 ，你必须要写成「`AT&T`」 ，还得转换网址内的 `&` 符号，如果你要链接到：

```
http://images.google.com/images?num=30&q=larry+bird
```

你必须要把网址转成：

```
http://images.google.com/images?num=30&amp;q=larry+bird
```

才能放到链接标签的 `href` 属性里。不用说也知道这很容易忘记，这也可能是 HTML 标准检查所检查到的错误中，数量最多的。

Markdown 允许你直接使用这些符号，它帮你自动转义字符。如果你使用 `&` 符号的作为 HTML 实体的一部分，那么它不会被转换，而在其它情况下，它则会被转换成 `&`。所以你如果要在文件中插入一个著作权的符号，你可以这样写：

```
&copy;
```

Markdown 将不会对这段文字做修改，但是如果你这样写：

```
AT&T
```

Markdown 就会将它转为：

```
AT&amp;T
```

类似的状况也会发生在 `<` 符号上，因为 Markdown 支持 [行内 HTML](https://markdown.com.cn/basic-syntax/#内联-html) ，如果你使用 `<` 符号作为 HTML 标签的分隔符，那 Markdown 也不会对它做任何转换，但是如果你是写：

```
4 < 5
```

Markdown 将会把它转换为：

```
4 &lt; 5
```

需要特别注意的是，在 Markdown 的块级元素和内联元素中， `<` 和 `&` 两个符号都会被自动转换成 HTML 实体，这项特性让你可以很容易地用 Markdown 写 HTML。（在 HTML 语法中，你要手动把所有的 `<` 和 `&` 都转换为 HTML 实体。）

## 十.Markdown 内嵌 HTML 标签

对于 Markdown 涵盖范围之外的标签，都可以直接在文件里面用 HTML 本身。如需使用 HTML，不需要额外标注这是 HTML 或是 Markdown，只需 HTML 标签添加到 Markdown 文本中即可。

#### 行级內联标签

HTML 的行级內联标签如 `<span>`、`<cite>`、`<del>` 不受限制，可以在 Markdown 的段落、列表或是标题里任意使用。依照个人习惯，甚至可以不用 Markdown 格式，而采用 HTML 标签来格式化。例如：如果比较喜欢 HTML 的 `<a>` 或 `<img>` 标签，可以直接使用这些标签，而不用 Markdown 提供的链接或是图片语法。当你需要更改元素的属性时（例如为文本指定颜色或更改图像的宽度），使用 HTML 标签更方便些。

HTML 行级內联标签和区块标签不同，在內联标签的范围内， Markdown 的语法是可以解析的。

```text
This **word** is bold. This <em>word</em> is italic.
```

渲染效果如下:

This **word** is bold. This _word_ is italic.

#### 区块标签

区块元素 ── 比如 `<div>`、`<table>`、`<pre>`、`<p>` 等标签，必须在前后加上空行，以便于内容区分。而且这些元素的开始与结尾标签，不可以用 tab 或是空白来缩进。Markdown 会自动识别这区块元素，避免在区块标签前后加上没有必要的 `<p>` 标签。

例如，在 Markdown 文件里加上一段 HTML 表格：

```
This is a regular paragraph.

<table>
    <tr>
        <td>Foo</td>
    </tr>
</table>

This is another regular paragraph.
```

请注意，Markdown 语法在 HTML 区块标签中将不会被进行处理。例如，你无法在 HTML 区块内使用 Markdown 形式的`*强调*`。

#### HTML 用法最佳实践

出于安全原因，并非所有 Markdown 应用程序都支持在 Markdown 文档中添加 HTML。如有疑问，请查看相应 Markdown 应用程序的手册。某些应用程序只支持 HTML 标签的子集。

对于 HTML 的块级元素 `<div>`、`<table>`、`<pre>` 和 `<p>`，请在其前后使用空行（blank lines）与其它内容进行分隔。尽量不要使用制表符（tabs）或空格（spaces）对 HTML 标签做缩进，否则将影响格式。

在 HTML 块级标签内不能使用 Markdown 语法。例如 `<p>italic and **bold**</p>` 将不起作用。

之后是扩展语法

## 十一.Markdown 表格

要添加表，请使用三个或多个连字符（`---`）创建每列的标题，并使用管道（`|`）分隔每列。您可以选择在表的任一端添加管道。

```text
| Syntax      | Description |
| ----------- | ----------- |
| Header      | Title       |
| Paragraph   | Text        |
```

| Syntax    | Description |
| :-------- | ----------- |
| Header    | Titile      |
| Paragraph | Text        |

//ty 打完第一行直接就把格式弄出来了，然后 ctrl+enter 可以下一行，然后 enter 到最后一行是退出

**Tip:** 使用连字符和管道创建表可能很麻烦。为了加快该过程，请尝试使用[Markdown Tables Generator](https://www.tablesgenerator.com/markdown_tables)。使用图形界面构建表，然后将生成的 Markdown 格式的文本复制到文件中。

#### 对齐

您可以通过在标题行中的连字符的左侧，右侧或两侧添加冒号（`:`），将列中的文本对齐到左侧，右侧或中心。

#### 格式化表格中的文字

您可以在表格中设置文本格式。例如，您可以添加链接，代码（仅反引号（```）中的单词或短语，而不是代码块）和强调。

您不能添加标题，块引用，列表，水平规则，图像或 HTML 标签。

您可以使用表格的 HTML 字符代码（`|`）在表中显示竖线（`|`）字符。

## 十二.Markdown 围栏代码块

之前说过了 ```

## 十三.Markdown 脚注

脚注使您可以添加注释和参考，而不会使文档正文混乱。当您创建脚注时，带有脚注的上标数字会出现在您添加脚注参考的位置。读者可以单击链接以跳至页面底部的脚注内容。

要创建脚注参考，请在方括号（`[^1]`）内添加插入符号和标识符。标识符可以是数字或单词，但不能包含空格或制表符。标识符仅将脚注参考与脚注本身相关联-在输出中，脚注按顺序编号。

在括号内使用另一个插入符号和数字添加脚注，并用冒号和文本（`[^1]: My footnote.`）。您不必在文档末尾添加脚注。您可以将它们放在除列表，块引号和表之类的其他元素之外的任何位置。

```text
Here's a simple footnote,[^1] and here's a longer one.[^bignote]

[^1]: This is the first footnote.

[^bignote]: Here's one with multiple paragraphs and code.

    Indent paragraphs to include them in the footnote.

    `{ my code }`

    Add as many paragraphs as you like.
```

呈现的输出如下所示：

Here's a simple footnote,[^1] and here's[^awa] a longer one.[^bignote]

[^1]: This is the first footnote.
[^bignote]:
[^awa]: `aaaa`

```
Indent paragraphs to include them in the footnote.

`{ my code }`

Add as many paragraphs as you like.
```

## 十四.Markdown 标题编号

许多 Markdown 处理器支持[标题](https://markdown.com.cn/basic-syntax/headings.html)的自定义 ID - 一些 Markdown 处理器会自动添加它们。添加自定义 ID 允许您直接链接到标题并使用 CSS 对其进行修改。要添加自定义标题 ID，请在与标题相同的行上用大括号括起该自定义 ID。

html 的话<h3 id="id1">My Great Heading</h3>

\### My Great Heading {#id}

### My Great Heading {#id2}

##### 链接到标题 ID (#headid)

通过创建带有数字符号（`#`）和自定义标题 ID 的[标准链接]((/basic-syntax/links.html)，可以链接到文件中具有自定义 ID 的标题。

| Markdown                      | HTML                                     | 预览效果                                                                       |
| ----------------------------- | ---------------------------------------- | ------------------------------------------------------------------------------ |
| `[Heading IDs](#heading-ids)` | `<a href="#heading-ids">Heading IDs</a>` | [Heading IDs](https://markdown.com.cn/extended-syntax/tables.html#heading-ids) |

其他网站可以通过将自定义标题 ID 添加到网页的完整 URL（例如`[Heading IDs](https://markdown.com.cn/extended-syntax/heading-ids.html#headid)`）来链接到标题。

[qwq](#id2) //感觉好像没用的样子？

## 十五.Markdown 定义列表

一些 Markdown 处理器允许您创建术语及其对应定义的*定义列表*。要创建定义列表，请在第一行上键入术语。在下一行，键入一个冒号，后跟一个空格和定义。

```text
First Term
: This is the definition of the first term.

Second Term
: This is one definition of the second term.
: This is another definition of the second term.
```

HTML 看起来像这样：

```html
<dl>
  <dt>First Term</dt>
  <dd>This is the definition of the first term.</dd>
  <dt>Second Term</dt>
  <dd>This is one definition of the second term.</dd>
  <dd>This is another definition of the second term.</dd>
</dl>
```

First Term

: This is aaa

//ty 不行

html 没问题

<dl>
  <dt>First Term</dt>
  <dd>This is the definition of the first term.</dd>
  <dt>Second Term</dt>
  <dd>This is one definition of the second term. </dd>
  <dd>This is another definition of the second term.</dd>
</dl>

## 十六.Markdown 删除线

您可以通过在单词中心放置一条水平线来删除单词。结果看起来像这样。此功能使您可以指示某些单词是一个错误，要从文档中删除。若要删除单词，请在单词前后使用两个波浪号`~~`。

```text
~~世界是平坦的。~~ 我们现在知道世界是圆的。
```

呈现的输出如下所示：

~~世界是平坦的。~~我们现在知道世界是圆的。

## 十七. Markdown 任务列表语法

任务列表使您可以创建带有复选框的项目列表。在支持任务列表的 Markdown 应用程序中，复选框将显示在内容旁边。要创建任务列表，请在任务列表项之前添加破折号`-`和方括号`[ ]`，并在`[ ]`前面加上空格。要选择一个复选框，请在方括号`[x]`之间添加 x 。

```text
- [x] Write the press release
- [ ] Update the website
- [ ] Contact the media
```

呈现的输出如下所示：

- [ ] qwq
- [x] awa

## 十八.Markdown 使用 Emoji 表情

有两种方法可以将表情符号添加到 Markdown 文件中：将表情符号复制并粘贴到 Markdown 格式的文本中，或者键入*emoji shortcodes*。

#### 复制和粘贴表情符号

在大多数情况下，您可以简单地从[Emojipedia (opens new window)](https://emojipedia.org/)等来源复制表情符号并将其粘贴到文档中。许多 Markdown 应用程序会自动以 Markdown 格式的文本显示表情符号。从 Markdown 应用程序导出的 HTML 和 PDF 文件应显示表情符号。

**Tip:** 如果您使用的是静态网站生成器，请确保将 HTML 页面编码为 UTF-8。.

#### 使用表情符号简码

一些 Markdown 应用程序允许您通过键入表情符号短代码来插入表情符号。这些以冒号开头和结尾，并包含表情符号的名称。

```text
去露营了！ :tent: 很快回来。

真好笑！ :joy:
```

呈现的输出如下所示：

去露营了！⛺ 很快回来。

真好笑！😂

**Note:** 注意：您可以使用此[表情符号简码列表](https://gist.github.com/rxaviers/7360908)，但请记住，表情符号简码因应用程序而异。有关更多信息，请参阅 Markdown 应用程序的文档。

## 最后:自动网址链接

许多 Markdown 处理器会自动将 URL 转换为链接。这意味着如果您输入http://www.example.com，即使您未[使用方括号](https://markdown.com.cn/basic-syntax/links.html)，您的Markdown处理器也会自动将其转换为链接。

```text
http://www.example.com
```

呈现的输出如下所示：

[http://www.example.com(opens new window)](http://www.example.com/)

#### 禁用自动 URL 链接

如果您不希望自动链接 URL，则可以通过将 URL 表示为带反引号的代码来删除该链接。

```text
`http://www.example.com`
```

呈现的输出如下所示：

`http://www.example.com`

好像 ty 并不支持，只是单纯当成代码块\*\*了
