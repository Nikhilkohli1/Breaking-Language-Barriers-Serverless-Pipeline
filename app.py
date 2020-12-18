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

region = 'us-east-1'
client_sf = boto3.client('stepfunctions')
s3_client = boto3.client('s3', region_name = region)
#TableName = "NERUserTokens"
TableName_ = "BLB_Step_function_Meta"
dynamodb = boto3.resource('dynamodb', region_name=region)
table_ = dynamodb.Table(TableName_)
dynamodb_client = boto3.client('dynamodb', region_name = region)

session_state = SessionState.get(checkboxed=False)

img_base = "https://www.htmlcsscolor.com/preview/128x128/{0}.png"

colors = (''.join(choices(ascii_uppercase[:6] + digits, k=6)) for _ in range(100))
st.set_page_config(layout="wide", page_title='Breaking Language Barriers')
st.title('Breaking Language Barriers')

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
            user_signup(name, uname, email, password)
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
    	st.markdown('**Upload audio file (mp3 | wav)**')
    	audio_f_u = st.file_uploader("")
    	if audio_f_u is not None:
            ScrapeorNot = 'No'
            dataframe = pd.read_csv(audio_f_u)
            t.write(dataframe)
    elif input_s == 'Audio links':
        st.markdown('**Upload CSV file with the Audio links to Scrape**')
        audio_l_u = st.file_uploader(" ")
        if audio_l_u is not None:
            ScrapeorNot = 'Yes'
            dataframe = pd.read_csv(audio_l_u)
            st.write(dataframe)
            for val in dataframe['Podcast_links']:
                st.write(val)
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
    submit = st.button('Run Pipeline')

    if submit: 
        try:
            if authorized or session_state.checkboxed:
                st.success("Hey {}, You are authorized to use our services".format(username))
                st.markdown("---")
                
                timestr = time.strftime("%Y%m%d-%H%M%S")
                User_selection_map = {"ScrapeorNot": ScrapeorNot,
                                    "Gender": Gender,
                                    "TranslationorNER": TranslationorNER,
                                    "Summarize": Summarize,
                                    "OutputAudio": OutputAudio,
                                    "MaskingEntity": MaskingEntity
                                        }

                sf_name = username + '_blb_master_execution' + timestr
                st.write(User_selection_map)

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
                st.write(response)
                
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
    
    try:
        item_resp = table_.scan(
                FilterExpression=Attr('Username').eq(username)
                    )
        for item in item_resp['Items']:
            prev_exec.append(item['Child_Step_function_Execution'])
            st.write(prev_exec)

    except:
            st.write('You have no Previous History')

    left_v, right_v = st.beta_columns(2)
    with left_v:
        execution_sel = st.selectbox('Select Pipeline Execution', prev_exec)
    with right_v:
        exec_lang = []
        item_resp = table_.scan(
        FilterExpression=Attr('Execution_name').eq(execution_sel)
                    )
        for item in item_resp['Items']:
            exec_lang.append(item['Langauges'])


        lang_s_v = st.multiselect("Select Translated languages to Visualize", exec_lang, default=exec_lang)
    

    #st.markdown('')
    #st.markdown('**Visualize Your Executions**')
    visualize = st.button('Visualize Output')
    if visualize:
        #include logic here for visualising all files for selected languages for selected execution
        st.write('Thanks for Visiting')
        for i in range(0,len(lang_s_v)):
            st.checkbox(lang_s_v[i], False)

st.write('')
st.write('')
st.write('')
st.write('')

st.markdown('Podcasts in Translated Langauges')
Viz1, Viz2, Viz3 = st.beta_columns(3)    
    
        
with Viz1:
    language1 = 'French'
    expand_l = st.beta_expander(language1)
    with expand_l:
        pass

with Viz2:
    language2 = 'German'
    expand_l = st.beta_expander(language2)
    with expand_l:
        pass

with Viz3:
    language3 = 'Hindi'
    expand_l = st.beta_expander(language3)
    with expand_l:
        pass

st.write('')
st.write('')
st.write('')
st.write('')
st.write('')

st.markdown('Podcasts after Masking Named Entities')
Viz4, Viz5 = st.beta_columns(2)    
    
        
with Viz4:

    expand_l = st.beta_expander("NER Visualization")
    with expand_l:
        pass

with Viz5:

    expand_l = st.beta_expander("Masked Podcast")
    with expand_l:
        pass

    



    



