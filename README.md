# Glow_Effect
イラストの仕上げのグロー効果を自動でつけるやつ.

<img src="https://user-images.githubusercontent.com/86103496/160360239-e9c42a42-1f16-4ad6-ba6c-a1ef900ee77e.jpg" width=320px> <img src="https://user-images.githubusercontent.com/86103496/160360250-45988d62-b15f-4d0c-9469-3b55cbc26c01.jpg" width=320px>

```
./glow_effect.py image.jpg
```

とすれば効果が適用された画像が "image_out.jpg" のように保存されます。　元イメージ名は何でも良いです。 png も可です。

## 仕組み
デジ絵でよく知られた、
```mermaid
flowchart LR
    id1(元絵) -- 複製 --> id2(グロー1) -- トーンカーブ -->  id3(グロー2) -- ぼかし --> id4(グロー3) -- スクリーン合成 --> id6(完成)
    id1(元絵) --> id6
```
をやってます。
