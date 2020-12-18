import streamlit as st
from string import ascii_uppercase, digits
from random import choices
import boto3
import json
import time
from datetime import datetime
from boto3.dynamodb.conditions import Key, Attr
from audio import get_welcome_msg
from login import authorize_user
from signup import user_signup, confirm_signup
import SessionState
import pandas as pd
from load_css import local_css
import ast

region = 'us-east-1'
client_sf = boto3.client('stepfunctions')
s3_client = boto3.client('s3', region_name = region)

bucket_name_save = 'blb-scraped-audio'


#TableName = "NERUserTokens"
TableName_ = "BLB_Step_function_Meta"
dynamodb = boto3.resource('dynamodb', region_name=region)
table_ = dynamodb.Table(TableName_)
dynamodb_client = boto3.client('dynamodb', region_name = region)

session_state = SessionState.get(checkboxed=False)
#session_state1 = SessionState.get(username='')

img_base = "https://www.htmlcsscolor.com/preview/128x128/{0}.png"

colors = (''.join(choices(ascii_uppercase[:6] + digits, k=6)) for _ in range(100))
st.set_page_config(layout="wide", page_title='Breaking Language Barriers')
st.title('Breaking Language Barriers')

local_css("style.css")

st.markdown("""
<style>
Body{
    color: white;
    background-color: #AF3C46;

}
</style>
    """, unsafe_allow_html=True)

#B4535C
#AF3C46
username = ''
authorized = False
with st.beta_container():
    for col in st.beta_columns(12):
        col.image(img_base.format(next(colors)), use_column_width=True)


tab1, tab2 = st.beta_columns(2)    
    
with tab1:

    expand_l = st.beta_expander("Login")
    with expand_l:
        username = st.text_input('Name')
        email = st.text_input('User Name')
        pwd = st.text_input('Password', type='password')
        login = st.button('Login')
        if (login):
            if session_state.checkboxed:
                st.success('Welcome back, You are already Logged in')
                authorized = True
                audio_bytes = get_welcome_msg(username)
                st.audio(audio_bytes, format='audio/ogg')
            else:
                authorized, uname = authorize_user(email, pwd)
                if authorized:
                    session_state.checkboxed = True
                    #session_state1.username = username
                    audio_bytes = get_welcome_msg(username)
                    st.success("You have successfully signed in as {}".format(username))
                    st.audio(audio_bytes, format='audio/ogg')
                    # save authorized info to session 

with tab2:
    expand_s = st.beta_expander("Signup")
    with expand_s:
        username = st.text_input('Full Name')
        uname = st.text_input('User Name ')
        email = st.text_input('Email')
        password = st.text_input('Password ', type='password')
        register = st.button('Register')
        if register:
            user_signup(username, uname, email, password)
        st.write('Enter the confirmation code sent to your Email to confirm Yourself')
        ccode = st.text_input('Confirmation Code')
        register2 = st.button('Confirm Your User')
        if register2:
            message, sign = confirm_signup(uname, ccode)
            st.success('Your email is verified, You can login now')

st.write('')
st.write('')
st.subheader('**Breaking Language Barriers: Translate Your Podcasts**')


st.write('')
st.write('')
st.write('Breaking Language Barriers is a Machine learning Pipeline which allows you to\
         Translate Your Podcasts into into multiple Languages, Summarize them, Extract Entities to mask them,\
         and convert them back into Speech \
         in various Languages, Gender & accents')

st.write('')
st.write('')




ScrapeorNot = ''
Gender = ''
Langauges = []
TranslationorNER = ''
Summarize = 'No'
OutputAudio = 'No'
Podcasts_links = []
MaskingEntity = []
Audio_Bytes = []

original_audio = ''
Audio_trans_map = {}
Transcript_file = ''
NER_Masking_map = {}
TranslationorNER_v = ''
language_v = []


def save_podcast_audio(Audio_Bytes, Username):
    scraped_audio_map = {}
    uploaded_podcasts = []
    timestr = time.strftime("%Y%m%d-%H%M%S")
    scrape_audio_tmp = "/tmp/" + Username + "_scraped_audio_" + timestr + '.mp3'
    scrape_audio = Username + "_scraped_audio_" + timestr + '.mp3'
    with open(scrape_audio_tmp, mode='bx') as f:
        f.write(Audio_Bytes)
    f.close()
    
    response = s3_client.upload_file(Filename=scrape_audio_tmp, Bucket=bucket_name_save, Key='English/{}'.format(scrape_audio))
    uploaded_podcasts.append(scrape_audio)

        #store metadata of files in dynamo
    scraped_audio_map['scraped_podcasts'] = uploaded_podcasts

    return scraped_audio_map


st.write('')
st.markdown('Welcome to Breaking Language Barriers - Services Section')
st.write('')
st.write('')
services_e = st.beta_expander("Our Services")
with services_e:
    st.markdown('')
    st.markdown('**Choose Input Type**')
    input_o = ['', 'Audio links', 'Audio files']
    input_s = st.selectbox('', options=input_o)
    if input_s == 'Audio files':
    	st.markdown('**Upload Podcast file (mp3 | wav)**')
    	audio_f_u = st.file_uploader("", type=['mp3','wav','zip','txt'])
    	if audio_f_u is not None:
            ScrapeorNot = 'No'
            audio_file = open(audio_f_u.name,"rb")
            audio_bytes = audio_file.read()
            audiof=st.audio(audio_bytes,format='audio/ogg',start_time=0)
            scraped_audio_map = save_podcast_audio(audio_bytes, username)
            #dataframe = pd.read_csv(audio_f_u)
            #t.write(dataframe)
    elif input_s == 'Audio links':
        st.markdown('**Upload CSV file with the Audio links to Scrape**')
        audio_l_u = st.file_uploader(" ")
        if audio_l_u is not None:
            ScrapeorNot = 'Yes'
            dataframe = pd.read_csv(audio_l_u)
            #st.write(dataframe)
            for val in dataframe['Podcast_links']:
                #st.write(val)
                Podcasts_links.append(val)
            st.markdown("---")
            st.markdown("**Select Services to be Applied**")
            st.write('')

    st.markdown('**What task would you like to Perform?**')
    radio_choice = st.radio('', ('Translate Podcasts in Multiple languages', 'Mask Audio content to Hide any Entity Information Specifics'))

    if radio_choice == 'Translate Podcasts in Multiple languages': 
        TranslationorNER = 'Translation'

        left_s, right_s = st.beta_columns(2)
        with left_s:
            st.markdown('**Summarize Podcasts/Articles/News :**')
        with right_s:
            summary_cbox = st.checkbox("Summarization", False)
        if summary_cbox:
            Summarize = 'Summarize'
        #st.write(Summarize)

        left_t, right_t = st.beta_columns(2)
        with left_t:
            st.markdown('**Translate Your content into Foreign Languages :**')
        with right_t:
            translation_cbox = st.checkbox("Language Translation", False)
            
        if translation_cbox:

            languges_all = ['Danish', 'Hindi', 'Chinese', 'French', 'German', 'Dutch', 'Italian', 'Spanish', 'English', 'Arabic', 'Japanese', 'Polish', 'Russian', 'Turkish', 'Portuguese']
            languges_d = ['Dutch', 'Hindi', 'French', 'German', 'Chinese']
            languages_s = st.multiselect("Select languages for Translation", languges_all, default=languges_d)
            Langauges = languages_s
            #st.write(Langauges)
        left_a, right_a = st.beta_columns(2)
        with left_a:
            st.markdown('**Convert your content into Podcasts with Gender of your choice :**')
        with right_a:
            audio_cbox = st.checkbox("Audio as Output", False)
        if audio_cbox:
            OutputAudio = 'Yes'
            gender_a = ['Male', 'Female']
            gender_s = st.selectbox("Select Gender for Podcasts", gender_a)
            Gender = gender_s
    elif radio_choice == 'Mask Audio content to Hide any Entity Information Specifics':
        TranslationorNER = 'NER'
        left_ner, right_ner = st.beta_columns(2)
        with left_ner:
            st.markdown('**Extract Entities and Expletive Mask selected PII Information :**')
        with right_ner:
            ner_cbox = st.checkbox("NER Expletive Masking", False)
        if ner_cbox:
            TranslationorNER = 'NER'
            entities_all = ['PERSON', 'ORGANIZATION','EVENT', 'TITLE', 'LOCATION', 'DATE', 'COMMERCIAL_ITEM']
            entities_d = ['PERSON', 'ORGANIZATION']
            entities_s = st.multiselect("Select entities for Expletive Masking", entities_all, default=entities_d)
            MaskingEntity = entities_s

        left_an, right_an = st.beta_columns(2)
        with left_an:
            st.markdown('**Convert your content into Podcasts with Gender of your choice :**')
        with right_an:
            neraudio_cbox = st.checkbox("Audio as Output", False)
        if neraudio_cbox:
            OutputAudio = 'Yes'
            gender_a = ['Male', 'Female']
            gender_s = st.selectbox("Select Gender for Podcasts", gender_a)
            Gender = gender_s
    st.write('')
    st.write('')
    st.write('Enter a Identifier for your Execution')
    username = st.text_input('Identifier')
    submit = st.button('Run Pipeline')

    if submit: 
        try:
            print('1')
            if authorized or session_state.checkboxed:
                st.write("Hey {}, You are authorized to use our services".format(username))
                st.markdown("---")
                print('2')
                timestr = time.strftime("%Y%m%d-%H%M%S")
                User_selection_map = {"ScrapeorNot": ScrapeorNot,
                                    "Gender": Gender,
                                    "TranslationorNER": TranslationorNER,
                                    "Summarize": Summarize,
                                    "OutputAudio": OutputAudio,
                                    "MaskingEntity": MaskingEntity
                                        }

                sf_name = username + '_blb_master_execution' + timestr
                #st.write(User_selection_map)
                print('3')

                sf_input = json.dumps({"body": {"User_selection_map": str(User_selection_map), 
                               "Langauges":str(Langauges),
                               "Username": username,
                               "Podcasts_links": str(Podcasts_links),
                               "ScrapeorNot": ScrapeorNot
                               }}, sort_keys=True)

                response = client_sf.start_execution(
                stateMachineArn='arn:aws:states:us-east-1:165885578631:stateMachine:BreakingBarriersMaster',
                name=sf_name,
                input= sf_input)
                #st.write(response)
                print('4')
                
                st.success('Pipeline Initiated, please check back after sometime to View/Download your files')
                
            else:
                st.success("You are not Authorized, please login or Register") 
        except:
            st.markdown('Please provide a valid URL/Podcast file')
            
st.write('')
st.write('')
st.write('')
st.write('')
st.write('')
st.write('')
st.write('')

visualize_e = st.beta_expander("Your Previous Documents")

with visualize_e:
    prev_exec = []
    st.write('Enter Your Identifier to View your Executions')
    username = st.text_input('Identifier ')

    
    try:
        #username = 'Nikhil'
        item_resp = table_.scan(
                FilterExpression=Attr('Username').eq(username)
                    )
        for item in item_resp['Items']:
            prev_exec.append(item['Child_Step_function_Execution'])
            #st.write(prev_exec)

    except:
            st.write('You have no Previous History')

    execution_sel = st.selectbox('Select Pipeline Execution', prev_exec)
    item_resp = table_.scan(
        FilterExpression=Attr('Child_Step_function_Execution').eq(execution_sel)
                    )
    #st.markdown('')
    #st.markdown('**Visualize Your Executions**')
    #visualize = st.button('Visualize Output')
    if execution_sel:

        
        TranslationorNER_v = item_resp['Items'][0]['TranslationorNER']
        if(TranslationorNER_v == 'Translation'):
            Audio_trans_map = ast.literal_eval(item_resp['Items'][0]['Audio_trans_map'])
            original_audio = ast.literal_eval(item_resp['Items'][0]['Podcast_map'])['Scraped_podcast']
            Transcript_file = item_resp['Items'][0]['Transcribe_file']
            language_v = ast.literal_eval(item_resp['Items'][0]['Langauges'])




        elif(TranslationorNER_v == 'NER'):
            NER_Masking_map = ast.literal_eval(item_resp['Items'][0]['NER_Masking_map'])
            original_audio = ast.literal_eval(item_resp['Items'][0]['Podcast_map'])['Scraped_podcast']
            Transcript_file = item_resp['Items'][0]['Transcribe_file']

        #include logic here for visualising all files for selected languages for selected execution
        #st.write('Thanks for Visiting')
        Summarize_v = item_resp['Items'][0]['Summarize']
        if(Summarize_v == 'Summarize'):
            Audio_summ_trans_map = ast.literal_eval(item_resp['Items'][0]['audio_summ_trans_map'])
            Transcript_file = item_resp['Items'][0]['Transcribe_file']
            language_vs = ast.literal_eval(item_resp['Items'][0]['Langauges'])

        

st.write('')
st.write('')
st.write('')
st.write('')

if execution_sel:
    if(TranslationorNER_v == 'Translation'):
        st.markdown('**Visualizing Language Translated Podcasts**')

        st.markdown('Original Podcast')

        bucket_1 = 'blb-translated-audio'
        bucket_2 = 'blb-scraped-audio'
        o_audio_file_name = original_audio
        audio_file_path =  'English/{}'.format(o_audio_file_name)
        response = s3_client.get_object(Bucket=bucket_2, Key=audio_file_path)
        audio_bytes = response['Body'].read()
        audiof=st.audio(audio_bytes,format='audio/ogg',start_time=0)

        st.markdown('Podcasts in Translated Langauges')
        
        if len(language_v) < 3:
            for i in range(3-len(language_v)):
                language_v.append('')

        Viz1 , Viz2, Viz3 = st.beta_columns(3) 
            
                
        with Viz1:
            language1 = language_v[0]
            expand_l = st.beta_expander(language1)
            with expand_l:
                audio_file_name = Audio_trans_map[language_v[0]]
                audio_file_path = language1 + '/{}'.format(audio_file_name)
                response = s3_client.get_object(Bucket=bucket_1, Key=audio_file_path)
                audio_bytes = response['Body'].read()
                audiof=st.audio(audio_bytes,format='audio/ogg',start_time=0)
                

        with Viz2:
            language2 = language_v[1]
            expand_l = st.beta_expander(language2)
            with expand_l:
                if language2 == '':
                    pass
                else:

                    audio_file_name = Audio_trans_map[language_v[1]]
                    audio_file_path = language2 + '/{}'.format(audio_file_name)
                    response = s3_client.get_object(Bucket=bucket_1, Key=audio_file_path)
                    audio_bytes = response['Body'].read()
                    audiof=st.audio(audio_bytes,format='audio/ogg',start_time=0)

        with Viz3:
            language3 = language_v[2]
            expand_l = st.beta_expander(language3)
            with expand_l:
                if language3 == '':
                    pass
                else:
                    audio_file_name = Audio_trans_map[language_v[2]]
                    audio_file_path = language3 + '/{}'.format(audio_file_name)
                    response = s3_client.get_object(Bucket=bucket_1, Key=audio_file_path)
                    audio_bytes = response['Body'].read()
                    audiof=st.audio(audio_bytes,format='audio/ogg',start_time=0)


    if(Summarize_v == 'Summarize'):
        st.markdown('Visualizing Summary & its Translated Podcasts')

        st.markdown('Original Podcast')

        bucket_1 = 'blb-summary-translated-audio'
        bucket_2 = 'blb-scraped-audio'

        o_audio_file_name = original_audio
        audio_file_path = 'English/{}'.format(o_audio_file_name)
        response = s3_client.get_object(Bucket=bucket_2, Key=audio_file_path)
        audio_bytes = response['Body'].read()
        audiof=st.audio(audio_bytes,format='audio/ogg',start_time=0)

        st.markdown('**Podcasts Summary in Translated Langauges**')
        
        if len(language_vs) < 3:
            for i in range(3-len(language_vs)):
                language_vs.append('')

        Vizs1 , Vizs2, Vizs3 = st.beta_columns(3) 
            
                
        with Vizs1:
            language1 = language_vs[0]
            expand_l = st.beta_expander(language1)
            with expand_l:
                audio_file_name = Audio_summ_trans_map[language_vs[0]]
                audio_file_path = language1 + '/{}'.format(audio_file_name)
                response = s3_client.get_object(Bucket=bucket_1, Key=audio_file_path)
                audio_bytes = response['Body'].read()
                audiof=st.audio(audio_bytes,format='audio/ogg',start_time=0)
                

        with Vizs2:
            language2 = language_vs[1]
            expand_l = st.beta_expander(language2)
            with expand_l:
                if language2 == '':
                    pass
                else:

                    audio_file_name = Audio_summ_trans_map[language_vs[1]]
                    audio_file_path = language2 + '/{}'.format(audio_file_name)
                    response = s3_client.get_object(Bucket=bucket_1, Key=audio_file_path)
                    audio_bytes = response['Body'].read()
                    audiof=st.audio(audio_bytes,format='audio/ogg',start_time=0)

        with Vizs3:
            language3 = language_vs[2]
            expand_l = st.beta_expander(language3)
            with expand_l:
                if language3 == '':
                    pass
                else:
                    audio_file_name = Audio_summ_trans_map[language_vs[2]]
                    audio_file_path = language3 + '/{}'.format(audio_file_name)
                    response = s3_client.get_object(Bucket=bucket_1, Key=audio_file_path)
                    audio_bytes = response['Body'].read()
                    audiof=st.audio(audio_bytes,format='audio/ogg',start_time=0)

    elif(TranslationorNER_v == 'NER'):
        st.write('')
        st.write('')
        st.markdown('**Visualizing NER Outputs**')

        st.markdown('Original Podcast')

        bucket_s = 'blb-scraped-audio'
        bucket_t = 'blb-ner-masked-text'
        bucket_a = 'blb-ner-masked-audio'

        o_audio_file_name = original_audio
        audio_file_path =  'English/{}'.format(o_audio_file_name)
        response = s3_client.get_object(Bucket=bucket_s, Key=audio_file_path)
        audio_bytes = response['Body'].read()
        audiof=st.audio(audio_bytes,format='audio/ogg',start_time=0)

        st.markdown('Podcasts after Masking Named Entities')
        Viz4, Viz5 = st.beta_columns(2)    
            
                
        with Viz4:

            expand_l = st.beta_expander("NER Visualization")
            with expand_l:
                ner_audio_file_name = NER_Masking_map['Entities_VIZ_file']
                audio_file_path =  'Original/{}'.format(ner_audio_file_name)
                response = s3_client.get_object(Bucket=bucket_t, Key=audio_file_path)
                orignial_html = response['Body'].read().decode('utf-8')

                color_lookup = {'PERSON':'tomato', 'ORGANIZATION':'aqua','EVENT':'dred', 'TITLE':'orchid', 'LOCATION':'blue', 'COMMERCIAL_ITEM':'red', 'DATE':'coral', 'QUANTITY':'pink', 'OTHER':'greenyellow'}
                st.markdown(orignial_html, unsafe_allow_html=True)

        with Viz5:

            expand_l = st.beta_expander("Masked Podcast")
            with expand_l:
                ner_audio_file_name = NER_Masking_map['Audio_masked_file']
                audio_file_path =  'English/{}'.format(ner_audio_file_name)
                response = s3_client.get_object(Bucket=bucket_a, Key=audio_file_path)
                audio_bytes = response['Body'].read()
                audiof=st.audio(audio_bytes,format='audio/ogg',start_time=0)

            



    



