/**
 * Quick Clip 工具
 * 
 * 使用方法:
 * 1. 打开 D:\go-to-marketing 目录下的 vault
 * 2. 在 Chrome 中打开任意网页
 * 3. 复制以下代码，在 Chrome 控制台 (F12) 中运行
 * 4. 网页内容会被保存到剪贴板，然后粘贴到 Obsidian 中
 */

// 这段代码可以创建一个书签工具
// 把下面的代码保存为书签的 URL

javascript:void(function(){
  var title = document.title;
  var url = window.location.href;
  var content = document.body.innerText;
  
  var md = '---\ntype: clip\nsource: "' + url + '"\ntitle: "' + title + '"\ntags: []\ningested: ' + new Date().toISOString().split('T')[0] + '\n---\n\n# ' + title + '\n\n> 被剪藏自: ' + url + '\n\n' + content.substring(0, 5000);
  
  navigator.clipboard.writeText(md).then(function(){
    alert('✓ 已复制到剪贴板！\n请在 Obsidian 中粘贴保存到 raw/clips/');
  });
})()
