# Glow_Effect
イラストの仕上げのグロー効果を自動でつけるやつです。

ちょっと雰囲気柔らかくしたいなってときに。

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

## オプション
```
usage: glow_effect.py [-h] [--suffix SUFFIX] [--quality QUALITY]
                      [--tone_curve_threshold TONE_CURVE_THRESHOLD]
                      [--tone_curve_delta TONE_CURVE_DELTA]
                      [--glow_bulr_size GLOW_BULR_SIZE]
                      [--glow_bulr_angle GLOW_BULR_ANGLE]
                      [--glow_strength GLOW_STRENGTH]
                      [--orig_gamma ORIG_GAMMA]
                      [--orig_brightness ORIG_BRIGHTNESS]
                      [--orig_color ORIG_COLOR] [--rgb_delta RGB_DELTA]
                      [--rgb_angle RGB_ANGLE] [--jpeg_quality JPEG_QUALITY]
                      file_name
```
### suffix (デフォルト: _out)
アウトプットファイル名の末尾です。

### quality (デフォルト: 85)
出力のjpg圧縮クオリティです。

### tone_curve_threshold (デフォルト: 0.9)
トーンカーブのグロー効果部のスレッショルドです。 明るさ (0-1) のどこから先を光らせるかを指定します。
|<img src=https://user-images.githubusercontent.com/86103496/160364346-edb4a9d1-4690-43f0-b239-90bfae602be0.jpg width=300px>|<img src=https://user-images.githubusercontent.com/86103496/160364897-89139f33-5ab5-4583-991b-52bbab5e2c7c.jpg width=300px>|
|:---:|:---:|
|0.5|0.95|

### tone_curve_delta (デフォルト: 0.04)
トーンカーブ急峻さです。小さいほど急峻になり、グローがくっきりします。
|<img src=https://user-images.githubusercontent.com/86103496/160366185-e25ec645-6106-4cfe-ba29-b72474f5c820.jpg width=300px>|<img src=https://user-images.githubusercontent.com/86103496/160365998-8fe7111d-a454-4132-ba8e-fbaa2d3907c6.jpg width=300px>|
|:---:|:---:|
|0.001|0.2|

### glow_bulr_size (デフォルト: 0.4)
グローのぼかし幅です。縦、横狭い側に対する%を指定します。
|<img src=https://user-images.githubusercontent.com/86103496/160366703-0dff9627-98c3-4231-9ddd-003f0bcfc941.jpg width=300px>|<img src=https://user-images.githubusercontent.com/86103496/160366812-69a88998-459b-4284-bef1-9cb21398425d.jpg width=300px>|
|:---:|:---:|
|0.1|2.0|

### glow_bulr_angle (デフォルト: None)
異方性ぼかしを適用したい場合に、角度を指定します。 指定がなければ通常のガウスぼかしです.
異方性ぼかしフィルタはPillowの標準機能じゃないので遅いです。

|<img src=https://user-images.githubusercontent.com/86103496/160360250-45988d62-b15f-4d0c-9469-3b55cbc26c01.jpg width=300px>|<img src=https://user-images.githubusercontent.com/86103496/160368039-a5a61554-9950-49ee-b2ff-d955a92c80fa.jpg width=300px>|
|:---:|:---:|
|None|45|

分かりづらいですが、＼ の方向の線に強くグローが入ります。

### glow_strength (デフォルト: 0.8)
そのままの意味です。 RGB 別々に指定することも出来ます。

|<img src=https://user-images.githubusercontent.com/86103496/160368647-bbd65953-4924-40e7-b83a-c268bf2ced6e.jpg width=300px>|<img src=https://user-images.githubusercontent.com/86103496/160368710-182267e9-9807-49dc-8165-0dac862f072d.jpg width=300px>|<img src=https://user-images.githubusercontent.com/86103496/160369278-84408e2d-9681-44a3-b423-9ac57d4796ab.jpg width=300px>|
|:---:|:---:|:---:|
|0.5|1.5|"1.0 0.5 0.5"|

### orig_gamma, orig_brightness, orig_color (デフォルト: 1.0)
スクリーン合成前のオリジナルイメージのガンマ値、輝度、彩度の調節パラメータです。
デフォルトでは何もしません。

### rgb_delta, rgb_angle (デフォルト: 0.0, 45)
グロー効果のR,G,Bをそれぞれずらします。 rgb_delta は縦、横狭い側に対する % を指定し、 rgb_angle でずらし角を指定します。

|<img src=https://user-images.githubusercontent.com/86103496/160370288-6d05d3c3-cd8f-4f04-93b4-d11e4f132886.jpg width=300px>|<img src=https://user-images.githubusercontent.com/86103496/160370194-cab11ebb-2428-48b2-93a6-2da8ad420866.jpg width=300px>|
|:---:|:---:|
|delta=0|delta=1.0, angle=-45|
