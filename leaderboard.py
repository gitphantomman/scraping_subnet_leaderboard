import gradio as gr
import pandas as pd
import matplotlib.pyplot as plt
from dataset_util import load_data, get_num_rows
import subnet_util
import datetime
import typing
import indexing_util
from io import BytesIO
FONT = """<link href="https://fonts.cdnfonts.com/css/intersect-c-brk" rel="stylesheet">"""
TITLE_FONT = """<link href="https://fonts.cdnfonts.com/css/promova" rel="stylesheet">"""
TITLE = """ <h1 align = "center" id = "space-title" class = "intersect"> D3 Subnet Leaderboard</h1> """
DESCRIPTION = """<marquee><h3 align= "center"> The D3 Subnet, standing for Decentralized Distributed Data Scraping subnet, plays a crucial role in the advancement of artificial intelligence by ensuring ample training data for all Bittensor AI networks. </h3></marquee>"""
IMAGE = """<a href="https://discord.com/channels/799672011265015819/1161764869280903240" target="_blank"><img src="https://cdn.discordapp.com/attachments/1204940599145267200/1227239850332131388/5CB42426-0E73-4D10-A66A-9E256C6A6183.png?ex=6627af2d&is=66153a2d&hm=02b9870618dd8e2e6bf62a0635f3cc8020221a0c7c2568138070f614e63a2068&" alt="D3 Subnet" style="margin: auto; width: 20%; border: 0;" /></a>"""

last_refresh = None
demo = gr.Blocks(css="""
                 .intersect {font-family: 'Intersect C BRK', sans-serif; font-size:40px} 
                 .promova {font-family: 'Promova', sans-serif; font-size:40px}
                 """)

twitter_text_dataset = load_data("bittensor-dataset/twitter-text-dataset")
twitter_text_num_rows = get_num_rows(twitter_text_dataset)
twitter_image_dataset = load_data("bittensor-dataset/twitter-image-dataset")
twitter_image_num_rows = get_num_rows(twitter_image_dataset)

tao_price = subnet_util.get_tao_price()
(subtensor, metagraph) = subnet_util.get_subtensor_and_metagraph()
last_refresh = datetime.datetime.now()
miners_data = subnet_util.get_subnet_data(subtensor, metagraph)



daily_indexing_data = indexing_util.get_all(indexing_util.daily_indexing)
daily_df = pd.DataFrame(daily_indexing_data, columns=['Date', 'Value'])
daily_df['Date'] = pd.to_datetime(daily_df['Date'].str.decode('utf-8'))
daily_df['Value'] = daily_df['Value'].astype(int)

hotkey_indexing_data = indexing_util.get_all(indexing_util.hotkey_indexing)
hotkey_df = pd.DataFrame(hotkey_indexing_data, columns=['Hotkey', 'Value'])
hotkey_df['Hotkey'] = hotkey_df['Hotkey'].str.decode('utf-8')
hotkey_df['Value'] = hotkey_df['Value'].astype(int)

hotkey_daily_indexing_data = indexing_util.get_all(indexing_util.hotkey_daily_indexing)
hotkey_daily_df = pd.DataFrame(hotkey_daily_indexing_data, columns=['Hotkey_Date', 'Value'])
hotkey_daily_df_= pd.DataFrame()
hotkey_daily_df_['Hotkey'] = hotkey_daily_df['Hotkey_Date'].str.decode('utf-8').str.split(' ').str[0]
hotkey_daily_df_['Date'] = hotkey_daily_df['Hotkey_Date'].str.decode('utf-8').str.split(' ').str[1]
hotkey_daily_df_['Value'] = hotkey_daily_df['Value'].astype(int)

print(hotkey_daily_df_)






def leaderboard_data(
    # show_stale: bool,
    # scores: typing.Dict[int, typing.Dict[str, typing.Optional[float | str]]],
    # competition_id: str,
):
    value = [
        [
            c.hotkey[0:8],
            c.uid,
            c.url,
            c.block,
        ]
        for c in miners_data
        # if c.incentive and c.url[0:8] == "https://"
    ]
    return value

with demo:
    gr.HTML(FONT)
    gr.HTML(TITLE_FONT)
    gr.HTML(TITLE)
    gr.HTML(IMAGE)
    gr.HTML(DESCRIPTION)

    with gr.Tabs():
        with gr.Accordion("Dataset Stats"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.HTML(f"<h2 align = 'center'  style = 'font-size: 25px' >Current Size of Text Dataset: <span style = 'font-size: 30px; color: green;'>{twitter_text_num_rows}</span></h2>")
                with gr.Column(scale=1):
                    gr.HTML(f"<h2 align = 'center' style = 'font-size: 25px' >Current Size of Image Dataset: <span style = 'font-size: 30px; color: green;'>{twitter_image_num_rows}</span></h2>")
        with gr.Accordion("Subnet Stats"):
            gr.HTML(f"""<h2 align = 'center' class="promova" style = 'font-size: 35px;' > Miner Stats</h2>""")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.BarPlot(
                        daily_df,
                        x="Date",
                        y="Value",
                        title="Daliy scraped data amount",
                        # color="Date",
                        tooltip=["Date", "Value"],
                        y_lim=[0, 1000],
                        x_title="Date",
                        y_title="Amount of data scraped",
                        height=500,
                        width=500,
                        scale=5,
                        color="Value",
                        color_legend_position="top",
                        # elem_classes="daily_scraped_data",
                    )
                with gr.Column(scale=1):
                    gr.BarPlot(
                        hotkey_df,
                        x="Hotkey",
                        y="Value",
                        title="Scraped data amount of each Miner",
                        # color="Date",
                        tooltip=["Hotkey", "Value"],
                        y_lim=[0, 1000],
                        x_title="Date",
                        y_title="Amount of data scraped",
                        height=500,
                        width=500,
                        scale=5,
                        color="Value",
                        x_label_angle=-30,
                        color_legend_position="top",
                        # elem_classes="daily_scraped_data",
                    )
            
            gr.ScatterPlot(
                hotkey_daily_df_,
                x="Date",
                y="Value",
                title="Daily scraped data amount of each Miner",
                # color="Date",
                tooltip=["Hotkey"],
                y_lim=[0, 1000],
                x_title="Date",
                y_title="Amount of data scraped",
                height=500,
                width=1000,
                scale=5,
                color="Hotkey",
                x_label_angle=-30,
                color_legend_position="top",
                # elem_classes="daily_scraped_data",
            )
        with gr.Tab(label="Miners Data"):
            class_denominator = sum(
                miners_data[i].incentive #TODO: emssion to incentive
                for i in range(0, min(10, len(miners_data)))
                if miners_data[i].incentive
            )
            class_values = {
                f"(uid={miners_data[i].uid}, hotkey={miners_data[i].hotkey[0:8]}) - {miners_data[i].url} · ${round(miners_data[i].emission * tao_price, 2):,} (τ{round(miners_data[i].emission, 2):,})": miners_data[i].incentive / class_denominator
                for i in range(0, min(10, len(miners_data)))
                if miners_data[i].incentive
            }
            gr.Label(
                label="Top 10 Miners",
                value=class_values,
                num_top_classes=10,
            )
        # miner_table = gr.components.Dataframe(
        #     value=miners_data
        # )
        with gr.Accordion("Miner stats"):
            gr.HTML(
                f"""<h3>{last_refresh.strftime("refreshed at %H:%M on %Y-%m-%d")}</h3>"""
            )
            # with gr.Tabs():
            #     for entry in miners_data:
            #         name = f"uid={entry.uid} : commit={entry.commit[0:8]} : url={entry.url}"
            #         with gr.Tab(name):
            #             gr.Chatbot()
            leaderboard_table = gr.components.Dataframe(
                value=leaderboard_data(),
                headers = [
                    "Hotkey",
                    "UID",
                    "Url",
                    "Block",
                ],
                datatype=[
                    "markdown",
                    "number",
                    "markdown",
                    "number",

                ],
                elem_id="leaderboard_table",
                interactive=False,
                visible=True,

            )
demo.launch()