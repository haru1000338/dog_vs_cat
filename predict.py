import os
import sys
from tensorflow.keras.applications.vgg16 import VGG16
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Input, Activation, Dropout, Flatten, Dense
from tensorflow.keras.preprocessing import image
import numpy as np

def main(filename=None):
    if filename is None:
        if len(sys.argv) == 2:
            filename = sys.argv[1]
        else:
            print("usage: python predict.py [filename]")
            return None, None
    
        # if len(sys.argv) != 2:
        #     print("usage: python predict.py [filename]")
        #     sys.exit(1)

    # filename = sys.argv[1]
    # print('input:', filename)

    try:
        result_dir = 'results'
        img_height, img_width = 150, 150
        channels = 3

        # VGG16モデル作成
        input_tensor = Input(shape=(img_height, img_width, channels))
        vgg16_model = VGG16(include_top=False, weights='imagenet', input_tensor=input_tensor)

        # FC
        top_model = Sequential()
        top_model.add(Flatten(input_shape=vgg16_model.output_shape[1:]))
        top_model.add(Dense(256, activation='relu'))
        top_model.add(Dropout(0.5))
        top_model.add(Dense(1, activation='sigmoid'))


        # VGG16とFCを接続
        model = Model(inputs=vgg16_model.input, outputs=top_model(vgg16_model.output))

        # 学習済みの重みをロード
        model.load_weights(os.path.join(result_dir, 'finetuning.weights.h5'))

        model.compile(loss='binary_crossentropy',
                    optimizer='adam',
                    metrics=['accuracy'])
        # model.summary()

        # 画像を読み込んで4次元テンソルへ変換
        img = image.load_img(filename, target_size=(img_height, img_width))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)

        # 学習時にImageDataGeneratorのrescaleで正規化したので同じ処理が必要！
        # これを忘れると結果がおかしくなるので注意
        x = x / 255.0

        # print(x)
        # print(x.shape)

        print("----------------------------------------------")
        #print('input:', filename)

        # クラスを予測
        # 入力は1枚の画像なので[0]のみ
        pred = model.predict(x)[0]
        raw_value = float(pred[0]) 
        print(f"予測値：{raw_value:.4f}")

        # 結果の解釈（0.5より大きければ犬、小さければ猫）
        if pred[0] > 0.5:
            prediction = "犬"
            probability = raw_value
            print(f"予測: 犬 (確率: {probability:.4f})")
        else:
            prediction = "猫"
            probability = 1 - raw_value
            print(f"予測: 猫 (確率: {probability:.4f})")

        return prediction, probability

    except Exception as e:
        print(f"Error: {e}")
        print("予測に失敗しました。")
        return None, None

if __name__ == "__main__":
    main()
