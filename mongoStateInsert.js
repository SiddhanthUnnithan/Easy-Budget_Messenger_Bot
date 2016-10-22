use budget

db.state.insert({
	"states": ["goal_desc", "goal_title", "goal_amount", "curr_balance"],
	"map": {
		"goal_desc": {
			"is_message_sent": false,
			"answer": null
		}, "goal_title": {
			"is_message_sent": false,
			"answer": null
		}, "goal_amount": {
			"is_message_sent": false,
			"answer": null
		}, "curr_balance": {
			"is_message_sent": false,
			"answer": null
		}
	}
})