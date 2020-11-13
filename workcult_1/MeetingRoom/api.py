from rest_framework import generics, permissions, viewsets, status, mixins
from rest_framework.response import Response
import os
# Import to send email
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives

from requests.exceptions import HTTPError
# The following import and then adding it to authentication classes is very important. Without this:
# the error was Authentication credentials were not provided.
# Took 24 hours to figure this out
from django.contrib.auth import login
from rest_framework.exceptions import PermissionDenied
from knox.auth import TokenAuthentication
from knox.models import AuthToken
from .models import MeetingRoom, MonthlyUsage, Invoice
from LocalUser.models import LocalUser, UserProfile, Company
from .serializers import MeetingRoomSerializer

from datetime import datetime, timezone, date, timedelta

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from rest_framework.exceptions import ValidationError

from django.core.files import File
from io import BytesIO

from . import my_payment
from . import makeinvoice, makeinvoice2

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



#
# class MeetingRoomView(generics.RetrieveUpdateDestroyAPIView):
# MAKE LOOKUP FIELD = COMPANY ??

from django.http import HttpResponse
from .utils import render_to_pdf

emailer = '''
    <body>
    <table class="mycontainer" width="100%" style="align-self: center;">
        <tr>
            <td align="center">
                <table class="workcultlogo" border="1" style="background-image: url(https://workcult.s3.ap-south-1.amazonaws.com/Emailer/newheaderimg.jpg);background-repeat: no-repeat;background-size: cover;background-blend-mode: lighten;padding: 200;width: 100%;">
                    <tr>
                        <td align="center">
                            <img class="myimg" src="https://workcult.s3.ap-south-1.amazonaws.com/Emailer/Workcult+Logo+Final.png" alt="" style="align-self: center;max-width: 500px;width: 100%;min-width: 200px;height: auto;">
                            <h1 class="workforce" style="color: white;padding-top: 20;">If you identify yourself as an independent workforce, we'd work best for you!</h1>
                        
                    </td></tr>
                    
                </table>
            </td>
            
        </tr>
        <table class="mytextdiv" style="white-space: nowrap;width: 100%;margin-top: 40px;padding-top: 150px;padding-bottom: 150px;background-image: url(https://workcult.s3.ap-south-1.amazonaws.com/Emailer/entrance.jpeg);background-blend-mode: lighten;background-size: cover;background-position: center;background-repeat: no-repeat;">
            
                                   <tr class="myul">
                                        <td style="white-space: nowrap;">
                                            <span class="dot1" style="height: 100px;width: 50px;background-color: #F0D27C;display: inline-block;border-top-right-radius: 50px;border-bottom-right-radius: 50px;"> </span>
                                        </td>
                                        <td class="mycstd" rowspan="4" style="white-space: normal;width: 50%;vertical-align: middle;border-right: 10px solid #ffffff;padding-left: 40px;padding-right: -10px;">
                                            <h1 class="mycs" style="color: white;font-size: 80;font-family: Arial, Helvetica;">
                                                A state of the art co-working space
                                            </h1> 
                                        </td>
                                        
                                        <td class="mycstd2" rowspan="4" style="white-space: normal;text-align: center;">
                                            <img src="https://workcult.s3.ap-south-1.amazonaws.com/Emailer/location3.png" alt="" class="locationimg" style="margin-bottom: -50px;width: 150px;"> 
                    
                                            <p class="mycs3" style="color: white;font-size: 50;font-family: Arial;font-weight: 100;">Viman Nagar, Pune</p>
                                        </td>
                                        
                                   </tr>
                                   <tr class="myul">
                                        <td style="white-space: nowrap;">
                                            <span class="dot2" style="height: 100px;width: 50px;background-color: #97D3C7;border-top-right-radius: 50px;border-bottom-right-radius: 50px;display: inline-block;"> </span>
                                        </td>
                                    </tr>  
                                    <tr class="myul">
                                        <td style="white-space: nowrap;">
                                            <span class="dot3" style="height: 100px;width: 50px;background-color: #8FB7DB;border-top-right-radius: 50px;border-bottom-right-radius: 50px;display: inline-block;"> </span>
                                        </td>
                                    </tr> 
                                    <tr class="myul">
                                        <td style="white-space: nowrap;">
                                            <span class="dot4" style="height: 100px;width: 50px;background-color: #F68B75;border-top-right-radius: 50px;border-bottom-right-radius: 50px;display: inline-block;"> </span>
                                        </td>
                                    </tr>                     
                                
            
                        
        
    
                    
                    
                
            

        </table>

        <table class="myseperator" width="100%" style="margin-top: 40px;margin-bottom: 40px;margin-left: 30px;">
            <tr>
                <td>
                    <span class="dot1a" style="min-height: 20px;min-width: 20px;background-color: #F0D27C;border-radius: 50%;display: inline-block;margin-right: 40px;"></span>
                    <span class="dot2a" style="min-height: 20px;min-width: 20px;background-color: #97D3C7;border-radius: 50%;display: inline-block;margin-right: 40px;"></span>
                    <span class="dot3a" style="min-height: 20px;min-width: 20px;background-color: #8FB7DB;border-radius: 50%;display: inline-block;margin-right: 40px;"></span>
                    <span class="dot4a" style="min-height: 20px;min-width: 20px;background-color: #F68B75;border-radius: 50%;display: inline-block;margin-right: 40px;"></span>
                    <span class="dot1a" style="min-height: 20px;min-width: 20px;background-color: #F0D27C;border-radius: 50%;display: inline-block;margin-right: 40px;"></span>
                    <span class="dot2a" style="min-height: 20px;min-width: 20px;background-color: #97D3C7;border-radius: 50%;display: inline-block;margin-right: 40px;"></span>
                    <span class="dot3a" style="min-height: 20px;min-width: 20px;background-color: #8FB7DB;border-radius: 50%;display: inline-block;margin-right: 40px;"></span>
                    <span class="dot4a" style="min-height: 20px;min-width: 20px;background-color: #F68B75;border-radius: 50%;display: inline-block;margin-right: 40px;"></span>
                </td>
            </tr>
        </table>

        <table class="nextcontent" style="height: 400px;background-color: #D9EFFC;width: 100%;padding-top: 20px;padding-bottom: 20px;padding-left: 20px;margin-top: 10px;margin-bottom: 10px;">
            <tr>
                <td class="workingman" style="width: 40%;">
                    <img src="https://workcult.s3.ap-south-1.amazonaws.com/Emailer/workingman2.png" alt="" class="workingmanimg" style="width: 400px;">
                </td>
                <td class="aboutus" style="display: inline-block;">
                    <h1 class="aboutusheader" style="color: #213E54;font-size: 50;font-family: Arial;text-align: right;font-weight: 900;">About Us</h1>
                    <p class="aboutuscontent" style="display: inline-block;color: grey;text-align: right;font-family: Arial;font-size: 25px;font-weight: 500;">Pune is at the pinnacle of the dynamic plug and play culture. 
                        At Workcult,  infrastructure joins hands with service to provide shared rental office spaces in congruence with the needs of this culture. 
                    </p> <br>
                    <p class="aboutuscontent" style="display: inline-block;color: grey;text-align: right;font-family: Arial;font-size: 25px;font-weight: 500;">
                        Imagine yourself sitting at a comfortable bureau in Viman Nagar, only a few yards away from the airport and the city’s sprawling IT Hub. 
                        If you like venturing away from meeting rooms, you’d be in luck- some of the city’s best 
                        hotels lie in your neighbourhood for a quick business rendezvous. 
                        Plug in as you like and work according to your terms as you experience the vibrance of a motivated community of hardworking professionals

                    </p>
                </td>
            </tr>
        </table>
                
        <table class="myseperator" width="100%" style="margin-top: 40px;margin-bottom: 40px;margin-left: 30px;">
            <tr>
                <td class="firsthalf">

                </td>
                <td class="secondhalf" style="text-align: right;">
                    <span class="dot1a" style="min-height: 20px;min-width: 20px;background-color: #F0D27C;border-radius: 50%;display: inline-block;margin-right: 40px;"></span>
                    <span class="dot2a" style="min-height: 20px;min-width: 20px;background-color: #97D3C7;border-radius: 50%;display: inline-block;margin-right: 40px;"></span>
                    <span class="dot3a" style="min-height: 20px;min-width: 20px;background-color: #8FB7DB;border-radius: 50%;display: inline-block;margin-right: 40px;"></span>
                    <span class="dot4a" style="min-height: 20px;min-width: 20px;background-color: #F68B75;border-radius: 50%;display: inline-block;margin-right: 40px;"></span>
                    <span class="dot1a" style="min-height: 20px;min-width: 20px;background-color: #F0D27C;border-radius: 50%;display: inline-block;margin-right: 40px;"></span>
                    <span class="dot2a" style="min-height: 20px;min-width: 20px;background-color: #97D3C7;border-radius: 50%;display: inline-block;margin-right: 40px;"></span>
                    <span class="dot3a" style="min-height: 20px;min-width: 20px;background-color: #8FB7DB;border-radius: 50%;display: inline-block;margin-right: 40px;"></span>
                    <span class="dot4a" style="min-height: 20px;min-width: 20px;background-color: #F68B75;border-radius: 50%;display: inline-block;margin-right: 40px;"></span>
                </td>
            </tr>
        </table>

        <table class="nextcontent2" style="width: 100%;background-color: #FFDAD4;padding-top: 20px;padding-bottom: 20px;padding-left: 20px;margin-top: 10px;margin-bottom: 10px;">
            <tr>
                <td class="offer" style="display: inline-block;padding: 50px;">
                    <h1 class="offerheader" style="color: #213E54;font-size: 70;font-family: Arial;font-weight: 900;">What we offer</h1>
                    <p class="offercontent" style="color: #213E54;font-size: 40px;font-family: Arial;font-weight: 100;">Workcult is a state of co-working space in Viman Nagar. We offer: </p>
                    <table class="myul4" style="display: inline-block;">
                        <tr>
                            <td class="mylinum" style="color: #213E54;height: 50;font-family: Arial;font-size: 20;font-weight: bold;">01</td>
                            <td class="mylicontent" style="padding-left: 20px;">
                                <p class="myliheader" style="font-weight: bold;display: inline;vertical-align: top;color: #213E54;font-family: Arial;font-size: 25;">Complete with elegant workdesks, </p>
                                <p class="mylinonheader" style="display: inline;vertical-align: top;color: #213E54;font-family: Arial;font-size: 25;">with ample plugins to support your talent</p>
                                
                            </td>
                        </tr>
                        <br>
                        
                        <tr>
                            <td class="mylinum" style="color: #213E54;height: 50;font-family: Arial;font-size: 20;font-weight: bold;">02</td>
                            <td class="mylicontent" style="padding-left: 20px;">
                                <br>
                                <p class="myliheader" style="font-weight: bold;display: inline;vertical-align: top;color: #213E54;font-family: Arial;font-size: 25;">High speed internet and power backup, </p>
                                <p class="mylinonheader" style="display: inline;vertical-align: top;color: #213E54;font-family: Arial;font-size: 25;">to mobilise and safeguard your smallest endeavours</p>
                            </td>
                        </tr>
                        <tr>
                            <td class="mylinum" style="color: #213E54;height: 50;font-family: Arial;font-size: 20;font-weight: bold;">03</td>
                            <td class="mylicontent" style="padding-left: 20px;">
                                <br>
                                <p class="myliheader" style="font-weight: bold;display: inline;vertical-align: top;color: #213E54;font-family: Arial;font-size: 25;">Online infrastructure: we offer to create website free of cost </p>
                                <p class="mylinonheader" style="display: inline;vertical-align: top;color: #213E54;font-family: Arial;font-size: 25;">to patrons who sign on a minimum for eight months. It takes an 
                                    army to sustain a growing enterprise and we like to provide whatever cavalry whenever we can.
                                </p>
                            </td>
                        </tr>
                        <tr>
                            <td class="mylinum" style="color: #213E54;height: 50;font-family: Arial;font-size: 20;font-weight: bold;">04</td>
                            <td class="mylicontent" style="padding-left: 20px;">
                                
                                <p class="myliheader" style="font-weight: bold;display: inline;vertical-align: top;color: #213E54;font-family: Arial;font-size: 25;">Parking spaces </p>
                                <p class="mylinonheader" style="display: inline;vertical-align: top;color: #213E54;font-family: Arial;font-size: 25;">and</p> 
                                <p class="myliheader" style="font-weight: bold;display: inline;vertical-align: top;color: #213E54;font-family: Arial;font-size: 25;">Dedicated meeting rooms </p>
                            </td>
                        </tr>
                        <tr>
                            <td class="mylinum" style="color: #213E54;height: 50;font-family: Arial;font-size: 20;font-weight: bold;">05</td>
                            <td class="mylicontent" style="padding-left: 20px;">
                                
                                <p class="myliheader" style="font-weight: bold;display: inline;vertical-align: top;color: #213E54;font-family: Arial;font-size: 25;">In-house coffee </p>
                                <p class="mylinonheader" style="display: inline;vertical-align: top;color: #213E54;font-family: Arial;font-size: 25;"> to keep your work brewing.
                                </p>
                            </td>
                        </tr>
                        <tr>
                            <td class="mylinum" style="color: #213E54;height: 50;font-family: Arial;font-size: 20;font-weight: bold;">06</td>
                            <td class="mylicontent" style="padding-left: 20px;">
                                
                                <p class="myliheader" style="font-weight: bold;display: inline;vertical-align: top;color: #213E54;font-family: Arial;font-size: 25;">Cleaning Staff. </p>
                                
                            </td>
                        </tr>
                    </table>
                </td>
                <td class="deskworkers" style="text-align: right;">
                    <img src="https://workcult.s3.ap-south-1.amazonaws.com/Emailer/deskworkers.png" alt="" class="deskworkersimg" style="width: 500px;">
                </td>
            </tr>
        </table>
        
        <table class="myseperator" width="100%" style="margin-top: 40px;margin-bottom: 40px;margin-left: 30px;">
            <tr>
                <td>
                    <span class="dot1a" style="min-height: 20px;min-width: 20px;background-color: #F0D27C;border-radius: 50%;display: inline-block;margin-right: 40px;"></span>
                    <span class="dot2a" style="min-height: 20px;min-width: 20px;background-color: #97D3C7;border-radius: 50%;display: inline-block;margin-right: 40px;"></span>
                    <span class="dot3a" style="min-height: 20px;min-width: 20px;background-color: #8FB7DB;border-radius: 50%;display: inline-block;margin-right: 40px;"></span>
                    <span class="dot4a" style="min-height: 20px;min-width: 20px;background-color: #F68B75;border-radius: 50%;display: inline-block;margin-right: 40px;"></span>
                    <span class="dot1a" style="min-height: 20px;min-width: 20px;background-color: #F0D27C;border-radius: 50%;display: inline-block;margin-right: 40px;"></span>
                    <span class="dot2a" style="min-height: 20px;min-width: 20px;background-color: #97D3C7;border-radius: 50%;display: inline-block;margin-right: 40px;"></span>
                    <span class="dot3a" style="min-height: 20px;min-width: 20px;background-color: #8FB7DB;border-radius: 50%;display: inline-block;margin-right: 40px;"></span>
                    <span class="dot4a" style="min-height: 20px;min-width: 20px;background-color: #F68B75;border-radius: 50%;display: inline-block;margin-right: 40px;"></span>
                </td>
            </tr>
        </table>
            
        <table class="nextcontent3" style="width: 100%;background-color: #F4E0AE;padding-top: 20px;padding-bottom: 20px;padding-left: 20px;margin-top: 10px;margin-bottom: 10px;">
            <tr>
                <td class="deskworkers" style="text-align: right;">
                    <img src="https://workcult.s3.ap-south-1.amazonaws.com/Emailer/uniqueimg.png" alt="" class="deskworkersimg" style="width: 500px;">
                </td>
                <td class="unique" style="display: inline-block;width: 100%;">
                    <h1 class="uniqueheader" style="color: #213E54;font-size: 70;font-family: Arial;font-weight: 900;">What makes us unique</h1>
                    <table class="myul4" style="display: inline-block;">
                        <tr>
                            <td class="myuniquenum">
                                <img src="https://workcult.s3.ap-south-1.amazonaws.com/Emailer/24x7access.png" alt="" class="access" style="width: 50px;">
                            </td>
                            <td class="myuniquelicontent" style="padding-left: 20px;">
                                <h3 class="uniqueliheader" style="display: inline;vertical-align: top;color: #213E54;font-family: Arial;font-size: 25;font-weight: bold;">Your work, your hours. Our Infrastructure  </h3>
                                <p class="uniquelinonheader" style="padding-top: 0;margin-top: 0;display: inline-block;vertical-align: top;color: #213E54;font-family: Arial;font-size: 25;">Workcult welcomes early birds and night owls alike, so we like to stay open 24x7</p>
                            </td>
                       </tr>
                       <tr>
                            <td class="myuniquenum">
                                <img src="https://workcult.s3.ap-south-1.amazonaws.com/Emailer/essentialsimg.png" alt="" class="access" style="width: 50px;">
                            </td>
                            <td class="myuniquelicontent" style="padding-left: 20px;">
                                <br>
                                <h3 class="uniqueliheader" style="display: inline;vertical-align: top;color: #213E54;font-family: Arial;font-size: 25;font-weight: bold;">Essentials only  </h3>
                            <p class="uniquelinonheader" style="padding-top: 0;margin-top: 0;display: inline-block;vertical-align: top;color: #213E54;font-family: Arial;font-size: 25;">Replete with power backup, a dedicated cleaning staff and office supplies, we're striving to make
                                Workcult the best co-working space in Viman Nagar
                            </p>
                        </td>
                        </tr>
                        <tr>
                            <td class="myuniquenum">
                                <img src="https://workcult.s3.ap-south-1.amazonaws.com/Emailer/sale.png" alt="" class="access" style="width: 50px;">
                            </td>
                            <td class="myuniquelicontent" style="padding-left: 20px;">
                                <br>
                                <h3 class="uniqueliheader" style="display: inline;vertical-align: top;color: #213E54;font-family: Arial;font-size: 25;font-weight: bold;">Great Prices  </h3>
                                <p class="uniquelinonheader" style="padding-top: 0;margin-top: 0;display: inline-block;vertical-align: top;color: #213E54;font-family: Arial;font-size: 25;">The thought of cheap co-working space in Viman Nagar might no longer
                                    be a distant dream! We strive to combine good service with affordability. Check out our prices here.
                                </p>
                            </td>
                        </tr>
                        <tr>
                            <td class="myuniquenum">
                                <img src="https://workcult.s3.ap-south-1.amazonaws.com/Emailer/customers.png" alt="" class="access" style="width: 50px;">
                            </td>
                            <td class="myuniquelicontent" style="padding-left: 20px;">
                                <br>
                                <h3 class="uniqueliheader" style="display: inline;vertical-align: top;color: #213E54;font-family: Arial;font-size: 25;font-weight: bold;">Meet different people from Different Walks of Life </h3>
                                <p class="uniquelinonheader" style="padding-top: 0;margin-top: 0;display: inline-block;vertical-align: top;color: #213E54;font-family: Arial;font-size: 25;">Become a part of a cult-oh, we mean "workcult"!
                                    Joining Workcult would mean that you’d be witnessing a confluence of vivid professions and 
                                    personalities without taking additional efforts.    
                                </p>
                            </td>
                        </tr>
                        <tr>
                            <td class="myuniquenum">
                                <img src="https://workcult.s3.ap-south-1.amazonaws.com/Emailer/pet.png" alt="" class="access" style="width: 50px;">
                            </td>
                            <td class="myuniquelicontent" style="padding-left: 20px;">
                                <br>
                                <h3 class="uniqueliheader" style="display: inline;vertical-align: top;color: #213E54;font-family: Arial;font-size: 25;font-weight: bold;">Pet friendly set up  </h3>
                                <p class="uniquelinonheader" style="padding-top: 0;margin-top: 0;display: inline-block;vertical-align: top;color: #213E54;font-family: Arial;font-size: 25;">We know how hard it is to leave your loved ones at home.
                                At Workcult you can celebrate, "bring your pet to work day" everyday!
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>

        <table class="seperator" width="100%" style="margin-top: 40px;margin-bottom: 40px;">
            <tr>
                <td class="mydiscount" style="text-align: center;"> 
                    <h1 class="discount" style="color: #213E54;font-size: 50;font-family: Arial;text-align: center;font-weight: 700;"> To avail a booking at a discounted rate of ₹400 for a day </h1>
                </td>
            </tr>
        </table>

        <table class="social" width="100%" style="background-color: #213E54;padding-top: 20px;padding-bottom: 20px;text-align: center;">
            <tr class="facebook">
                <td>
                    <p class="fbcontent" style="display: inline;vertical-align: 15px;font-family: Arial;font-size: 25;color: white;">Like us on </p>
                    <img src="https://workcult.s3.ap-south-1.amazonaws.com/Emailer/facebook-icon.png" alt="" class="fbicon" style="width: 55px;text-align: center;margin-left: 10px;margin-right: 10px;">
                    <p class="fbcontent" style="display: inline;vertical-align: 15px;font-family: Arial;font-size: 25;color: white;">@workcult123</p>
                </td>
            </tr>

            <tr class="insidesocial">
                <td>
                    <span class="dot1a circles" style="min-height: 20px;min-width: 20px;background-color: #F0D27C;border-radius: 50%;display: inline-block;margin-right: 40px;margin-top: 20px;margin-bottom: 20px;"> </span> 
                            <span class="dot2a circles" style="min-height: 20px;min-width: 20px;background-color: #97D3C7;border-radius: 50%;display: inline-block;margin-right: 40px;margin-top: 20px;margin-bottom: 20px;"> </span> 
                            <span class="dot3a circles" style="min-height: 20px;min-width: 20px;background-color: #8FB7DB;border-radius: 50%;display: inline-block;margin-right: 40px;margin-top: 20px;margin-bottom: 20px;"> </span> 
                            <span class="dot4a circles" style="min-height: 20px;min-width: 20px;background-color: #F68B75;border-radius: 50%;display: inline-block;margin-right: 40px;margin-top: 20px;margin-bottom: 20px;"> </span>
                            <span class="dot1a circles" style="min-height: 20px;min-width: 20px;background-color: #F0D27C;border-radius: 50%;display: inline-block;margin-right: 40px;margin-top: 20px;margin-bottom: 20px;"> </span> 
                            <span class="dot2a circles" style="min-height: 20px;min-width: 20px;background-color: #97D3C7;border-radius: 50%;display: inline-block;margin-right: 40px;margin-top: 20px;margin-bottom: 20px;"> </span> 
                            <span class="dot3a circles" style="min-height: 20px;min-width: 20px;background-color: #8FB7DB;border-radius: 50%;display: inline-block;margin-right: 40px;margin-top: 20px;margin-bottom: 20px;"> </span> 
                            <span class="dot4a circles" style="min-height: 20px;min-width: 20px;background-color: #F68B75;border-radius: 50%;display: inline-block;margin-right: 40px;margin-top: 20px;margin-bottom: 20px;"> </span>
                </td>
            </tr>

            <tr class="instagram">
                <td>
                    <p class="instacontent" style="display: inline;vertical-align: 15px;font-family: Arial;font-size: 25;color: white;padding-left: 40px;">Follow us on </p>
                    <img src="https://workcult.s3.ap-south-1.amazonaws.com/Emailer/instagram-logo.png" alt="" class="instaicon" style="width: 40px;margin-left: 10px;margin-right: 10px;">
                    <p class="fbcontent" style="display: inline;vertical-align: 15px;font-family: Arial;font-size: 25;color: white;">@workcult_coworks</p>
                </td>
            </tr>

        </table>
    </table>
</body>
'''

class MeetingRoomAPIView(
                    viewsets.GenericViewSet,
                    viewsets.mixins.ListModelMixin,
                    # viewsets.mixins.UpdateModelMixin,
                    viewsets.mixins.RetrieveModelMixin,
                    viewsets.mixins.DestroyModelMixin):

    serializer_class = MeetingRoomSerializer
    queryset = MeetingRoom.objects.all()

    def get_queryset(self):
        now = datetime.now(timezone.utc)
        # ?checkdate=2020-04-10 is passed in url at the end
        check_date = self.request.query_params.get('checkdate', None)

        if check_date:
            new_date = datetime.strptime(check_date, '%Y-%m-%d').date()
        else:
            new_date = now

        check_month = new_date.strftime("%m")
        check_year = new_date.strftime("%Y")
        check_day = new_date.strftime("%d")

        print(
            "CHECK_MONTH = " + str(check_month) + " " +
            "CHECK_YEAR = " + str(check_year) + " " +
            "CHECK_DAY = " + str(check_day) + " "
        )

        qs = MeetingRoom.objects.filter(
            start__year__gte=check_year,
            start__month__gte=check_month,
            start__day__gte=check_day,
            end__year__lte=check_year,
            end__month__lte=check_month,
            end__day__lte=check_day
        )
        print("QS = " + str(qs))
        if not qs:
            raise ValidationError("No bookings")
        return qs

    def perform_destroy(self, instance, from_admin=False):
        print("FROM ADMIN = " + str(from_admin))
        if self.request.user.is_admin:
            # self.perform_destroy(instance)
            super().perform_destroy(instance)
        elif from_admin:
            instance.delete(instance)
            # self.perform_destroy(instance)
        else:
            raise ValidationError("You cannot delete the booking")

    def create(self, request, *args, **kwargs):
        print("IN CREATE")
        print(request.data)
        # now = datetime.now(timezone.utc)
        start = request.data.get("start")
        end = request.data.get("end")
        print("RECEIVED START AND END AS "+ str(start) + " and " + str(end))
        if start == ":00" :
            raise ValidationError("The start date or time is incorrect")
        elif end == ":00":
            raise ValidationError("The end date or time is incorrect")
        new_start = self.convert_to_date(start)
        new_end = self.convert_to_date(end)

        now = datetime.now(timezone.utc)

        # qs = self.get_queryset()
        qs = my_queryset()
        # print("qs = " + str(qs))

        if not qs:
            print("NO QS!!")

        new_start2 = new_start.astimezone(timezone.utc)
        new_end2 = new_end.astimezone(timezone.utc)

        # print("NEW_START2 = " + str(new_start2))
        # print("NEW_END2 = " + str(new_end2))
        # new_now = datetime.timestamp()
        if new_start2 < now:
            raise ValidationError("Invalid time")
        if new_end2 < now:
            raise ValidationError("End time cannot be of the past")
        if new_end2 < new_start2:
            raise ValidationError("end time cannot be less than start time")

        for booked in qs:
            # print("BOOKED.START = " + str(booked.start))
            # print("END.START = " + str(booked.end))
            if new_start2 >= booked.start:
                if new_start2 <= booked.end:
                    raise ValidationError("From start Already booked")

            if new_end2 >= booked.start:
                if new_end2 <= booked.end:
                    raise ValidationError("From end Already booked ")

            if new_start2 <= booked.start:
                if new_end2 >= booked.start:
                    raise ValidationError("Again already end booked ")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        booking_month = new_start2.strftime("%m")
        booking_year = new_start2.strftime("%Y")
        booking_month_year = booking_month+"-"+booking_year
        print("THE BOOKING MONTH AND YEAR ARE = " + str(booking_month) + "-" + str(booking_year))

        print("request.data['company'] = " + str(request.data['company']))
        # print("The value is = " + (request.user.profile_id.company_name))

        try:
            print(str(request.user))
            myprofile_id = request.user.profile_id
        except:
            raise ValidationError("Cannot make the booking!!")

        if request.data['company'] != (request.user.profile_id.company_name.id):
            if request.user.is_admin:
                pass
            else:
                raise PermissionDenied("You cannot make bookings for other companies!")

        allotted = request.user.profile_id.company_name.allotted
        tdelta = new_end2 - new_start2
        minutes = tdelta.total_seconds() / 60

        print("THE ALLOTTED TIME IS : " + str(allotted))
        print("MINTUES = " + str(minutes))

        # GET COMPANY AND USER DETAILS
        company_name = request.user.profile_id.company_name
        company_address = request.user.profile_id.company_name.address
        gst = request.user.profile_id.company_name.gst
        hourly_rate = request.user.profile_id.company_name.hourly_rate
        email = request.user.profile_id.email
        user_first_name = request.user.profile_id.first_name


        try:
            monthly_query = MonthlyUsage.objects.get(
                company=company_name,
                month__iexact=booking_month_year
            )
        except MonthlyUsage.DoesNotExist:

            monthly_query = MonthlyUsage.objects.create(
                month=booking_month_year,
                company=company_name,
                used_this_month=0,
                used_till_date=0
            )
        current_invoice_number = Invoice.objects.last().invoice_number
        current_invoice_number = int(current_invoice_number)

        count = 0

        new_current_invoice_number = current_invoice_number + 1
        new_current_invoice_number2 = new_current_invoice_number
        while (new_current_invoice_number > 0):
            count = count + 1
            new_current_invoice_number = new_current_invoice_number // 10

        zeroes = "00000"
        new_zeroes = zeroes[count:]
        print("NEW ZEROES = " + new_zeroes)
        print("NEW INVOCE NUMBER BEFORE ADDING = " + str(new_current_invoice_number2))
        new_invoice_number = new_zeroes + str(new_current_invoice_number2)
        print("NEW INVOCE NUMBER AFTER ADDING = " + str(new_current_invoice_number2))

        if monthly_query.used_this_month > allotted:
            monthly_usage_object = update_monthly_usage_object(monthly_query, minutes)
            if monthly_usage_object:
                instance = serializer.save()
                print("serailizer data = " + str(serializer.data))



                try:
                    today_date = now.date()
                    due_date = today_date + timedelta(5)

                    print("TDAY DATE = " + str(today_date))
                    print("DUE DATE = " + str(due_date))

                    total_amount = (minutes/60) * hourly_rate

                    # Do payment
                    my_payment.do_payment(company_name.company_name, email, total_amount)

                    # raise ValueError("HEYEYYYYY WAITTTT")

                    res_attach = letscreate3(mydata={
                        "company": company_name,
                        "company_address": company_address,
                        "gst": gst,
                        "hourly_rate": hourly_rate,
                        "start": start,
                        "end": end,
                        "hours": minutes/60,
                        "total_amount": total_amount,
                        "invoice_number": new_invoice_number,
                        "id": instance,
                        "today_date": datetime.strftime(today_date, '%d %B, %Y'),
                        "due_date": datetime.strftime(due_date, '%d %B, %Y')
                    })

                    # The process of sending emails

                    subject = "Welcome to FootBuys!!"
                    message = "Hi " + user_first_name + ", \nThank you for registering with us. Glad to have you with us.\n\n\n\n\n\n\n\n This is an autogenerated email. Please do not try to revert back"
                    # message = emailer.replace(" ''' ", "")

                    from_mail = settings.EMAIL_HOST_USER
                    to_list = [email, settings.EMAIL_HOST_USER]

                    draft_mail = EmailMessage(subject, message, from_mail, to_list)
                    draft_mail.attach_file(res_attach)
                    check_mail = draft_mail.send()

                    # sending_email()

                    # check_mail = send_mail(subject, message, from_mail, to_list, fail_silently=True)
                    # print(str(check_mail))
                    # serializer.save(allowed=True)
                except ValueError:
                    # self.perform_destroy(serializer, from_admin=True)
                    print("DELTEDD!!!! VALUE ERROR!!")
                    instance.delete()
                    # serializer.delete()
            else:
                raise ValidationError("MONHTLY USAGE OBJECT IN PDF")
        else:
            avaialable_time = allotted - monthly_query.used_this_month
            print("AVAILABLE TIME = " + str(avaialable_time))

            if avaialable_time >= minutes:
                # monthly_usage_object = create_monthly_usage_object(booking_month_year, minutes, company_name)
                monthly_usage_object = update_monthly_usage_object(monthly_query, minutes)
                if monthly_usage_object:
                    serializer.save(allowed=True)
                else:
                    raise ValidationError("MONHTLY USAGE OBJECT ERROR NO PDF")
            else:
                print("IN INVOICE CREATION PHASE")

                today_date = now.date()
                due_date = today_date + timedelta(5)

                print("TDAY DATE = " + str(today_date))
                print("DUE DATE = " + str(due_date))


                monthly_usage_object = update_monthly_usage_object(monthly_query, minutes)
                if monthly_usage_object:
                    instance = serializer.save()
                    print("serailizer data = " + str(serializer.data))
                    try:
                        total_amount = ((minutes - avaialable_time) / 60) * hourly_rate

                        # Do payment
                        my_payment.do_payment(company_name.company_name, email, total_amount)

                        res_attach = letscreate3(mydata={
                            "company": company_name,
                            "start": start,
                            "end": end,
                            "hours": (minutes - avaialable_time)/60,
                            "total_amount": total_amount,
                            "invoice_number": new_invoice_number,
                            "id": instance,
                            "today_date": datetime.strftime(today_date, '%d %b, %Y'),
                            "due_date": datetime.strftime(due_date, '%d %b, %Y')
                        })

                        # The process of sending emails
                        subject = "Welcome to FootBuys!!"
                        message = "Hi " + user_first_name + ", \nThank you for registering with us. Glad to have you with us.\n\n\n\n\n\n\n\n This is an autogenerated email. Please do not try to revert back"
                        from_mail = settings.EMAIL_HOST_USER
                        to_list = [email, settings.EMAIL_HOST_USER]

                        draft_mail = EmailMessage(subject, message, from_mail, to_list)
                        draft_mail.attach_file(res_attach)
                        check_mail = draft_mail.send()
                        print(str(check_mail))

                    except ValueError:
                        # self.perform_destroy(serializer, from_admin=True)
                        print("DELTEDD!!!! VALUE ERROR!!")
                        instance.delete()
                        # serializer.delete()
                else:
                    raise ValidationError("MONHTLY USAGE OBJECT IN PDF")


                # monthly_usage_object = create_monthly_usage_object(booking_month_year, minutes, company_name)

                # raise ValidationError("You will have to pay first for the booking")
            # serializer.save()

        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def convert_to_date(self, init_date):
        # datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
        return datetime.strptime(init_date, '%Y-%m-%d %H:%M:%S')

    # def update(self, request, *args, **kwargs):
    #     return self.partial_update(request, *args, **kwargs)
    #

    # def partial_update(self, request, *args, **kwargs):
    #     kwargs['partial'] = True
    #     return self.update(request, *args, **kwargs)


def get_profile_id(user_id):
    qs = LocalUser.objects.get(id=user_id)
    profile_id = qs.profile_id
    return profile_id


def get_company_name(profile_id):
    qs = UserProfile.objects.get(id=profile_id.id)
    return qs.company_name


def my_queryset():
    now = datetime.now(timezone.utc)
    # ?checkdate=2020-04-10 is passed in url at the end
    # check_date = self.request.query_params.get('checkdate', None)

    # if check_date:
    #     new_date = datetime.strptime(check_date, '%Y-%m-%d').date()
    # else:
    new_date = now

    check_month = new_date.strftime("%m")
    check_year = new_date.strftime("%Y")
    check_day = new_date.strftime("%d")

    qs = MeetingRoom.objects.filter(
        start__year__gte=check_year,
        start__month__gte=check_month,
        start__day__gte=check_day,
        end__year__lte=check_year,
        end__month__lte=check_month,
        end__day__lte=check_day
    )

    return qs


def create_monthly_usage_object(booking_month_year, minutes, company_name):
    try:
        monthly_query = MonthlyUsage.objects.get(
            company=company_name,
            month__iexact=booking_month_year
        )
        if monthly_query:
            print("MONTHLY QUERY = " + str(monthly_query.used_this_month))
            monthly_query.used_this_month = monthly_query.used_this_month + minutes
            monthly_query.used_till_date = monthly_query.used_till_date + minutes
            monthly_query.save()
            print(" IN CREATE NOW MONTHLY QUERY = " + str(monthly_query.used_this_month))
            return True
    except MonthlyUsage.DoesNotExist:

        monthly_query2 = MonthlyUsage.objects.create(
            month=booking_month_year,
            company=company_name,
            used_this_month=minutes,
            used_till_date=minutes
        )
        if monthly_query2:
            print("now created")
            return True
        else:
            return False


def update_monthly_usage_object(monthly_usage_object, minutes):
    monthly_usage_object.used_this_month = monthly_usage_object.used_this_month + minutes
    monthly_usage_object.used_till_date = monthly_usage_object.used_till_date + minutes
    monthly_usage_object.save()
    print(" IN UPDATE NOW MONTHLY QUERY = " + str(monthly_usage_object.used_this_month))
    return True


class MeetingRoomTest(viewsets.GenericViewSet,
                    viewsets.mixins.ListModelMixin,
                    # viewsets.mixins.UpdateModelMixin,
                    viewsets.mixins.RetrieveModelMixin,
                    viewsets.mixins.DestroyModelMixin):
    serializer_class = MeetingRoomSerializer
    queryset = MeetingRoom.objects.all()

    def get_queryset(self):

        # company_razorpay = self.request.user.profile_id.company_name.company_razorpay
        # my_payment.get_customer(company_razorpay)
        # my_payment.create_invoice(company_razorpay, minutes=120)

        makeinvoice2.letscreate2(self.request)

        now = datetime.now(timezone.utc)
        # ?checkdate=2020-04-10 is passed in url at the end
        check_date = self.request.query_params.get('checkdate', None)

        if check_date:
            new_date = datetime.strptime(check_date, '%Y-%m-%d').date()
        else:
            new_date = now

        check_month = new_date.strftime("%m")
        check_year = new_date.strftime("%Y")
        check_day = new_date.strftime("%d")

        qs = MeetingRoom.objects.filter(
            start__year__gte=check_year,
            start__month__gte=check_month,
            start__day__gte=check_day,
            end__year__lte=check_year,
            end__month__lte=check_month,
            end__day__lte=check_day
        )
        if not qs:
            raise ValidationError("No bookings")
        return qs


def letscreate3(mydata):
    if mydata:
        data = mydata
    else:
        data = {
            'today': datetime.now(timezone.utc),
            'amount': 39.99,
            'customer_name': 'Cooper Mann',
            'order_id': 1233434,
        }
    pdf = render_to_pdf('template.html', data)
    # print("FOR PDF = ")
    # for key, value in pdf.items():
    #     print("KEY=" + str(key))
    #     print("VALUE = " + str(value))
    #     print("\n")

    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "MyInvoice_%s.pdf" % ("125")
        content = "attachment; filename='%s'" % (filename)
        response['Content-Length'] = len(response.content)
        print("AFTER DOWNLOAD")
        # download = request.GET.get("download")
        # if download:
        #
        #     print("AFTER DOWNLOAD")
        #     response['Content-Length'] = len(response.content)
        #     content = "attachment; filename='%s'" % (filename)
        #     # response.content.decode('utf-8').strip()

        response['Content-Disposition'] = content
        last_meeting_roo = MeetingRoom.objects.last()

        new_qs = Invoice(
            invoice_number=data['invoice_number'],
            meeting_room=data['id'],
        )

        where = new_qs.invoice_file.save(filename, File(BytesIO(response.content)))
        # new_qs.save()
        print("WHERE = " + str(where))
        my_new_file_obj = (filename, File(BytesIO(response.content)))
        # return my_new_file_obj

        print("NEW QS = " + str(new_qs))
        for key, value in response.items():
            print("KEY=" + str(key))
            print("VALUE = " + str(value))
            print("\n")
        # print(*response)
        pdf.close()
        # response.close()
        # return response
        # return my_new_file_obj
        return str(new_qs.invoice_file.url)
    return HttpResponse("Not found")
    print("OUTSIDE IF PDF")


def sending_email(request):

    to_list = ["anup2000ster@gmail.com",]

    # draft_mail = EmailMessage(subject="LINK", message=part1, from_mail="workcult07@gmail.com", to_list=to_list, html_message=part2)
    # draft_mail.send()
    print(str(settings.DEFAULT_FROM_EMAIL))
    eamil_message = EmailMultiAlternatives(subject="new  linik", body=emailer, from_email="Workcult<workcult07@gmail.com>", to=to_list)
    eamil_message.content_subtype = 'html'
    eamil_message.send()
    # send_mail(subject="new  linik", message="hey", from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=to_list, html_message=emailer)
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    # s.sendmail(me, you, msg.as_string())
    # s.quit()
