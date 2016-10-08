from flask import *

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def main_route():
	
	return "Test"
