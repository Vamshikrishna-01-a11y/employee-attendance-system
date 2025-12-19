from attendance import login, logout, generate_report, auto_logout

while True:
    print("\n1.Login")
    print("2.Logout")
    print("3.Daily Attendance Report")
    print("4.Auto Logout (7 PM)")
    print("5.Exit")

    choice = input("Enter choice: ")

    if choice == "1":
        login(int(input("Employee ID: ")))

    elif choice == "2":
        logout(int(input("Employee ID: ")))

    elif choice == "3":
        generate_report()

    elif choice == "4":
        auto_logout()
        print("Auto logout completed")

    elif choice == "5":
        print("System closed")
        break

    else:
        print("Invalid option")
