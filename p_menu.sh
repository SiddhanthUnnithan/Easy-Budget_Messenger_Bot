# logic for creating persistent menu
# this doesn't need to be created every time the server is instantiated
page_access_token=$1

curl -X POST -H "Content-Type: application/json" -d '{
	"setting_type": "call_to_actions",
	"thread_state": "existing_thread",
	"call_to_actions":[
    {
      "type":"web_url",
      "title":"View Website",
      "url": "http://prospercanada.org/",
      "webview_height_ratio": "full",
      "messenger_extensions": true
    },
    {
      "type":"web_url",
      "title":"View Facebook Page",
      "url":"https://www.facebook.com/Easy_Budget_V2-365381957186405/",
      "webview_height_ratio": "full",
      "messenger_extensions": true
    }
  ]
}' "https://graph.facebook.com/v2.6/me/thread_settings?access_token=$page_access_token"