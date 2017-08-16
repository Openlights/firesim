import QtQuick 2.0

Column {
    id: labeledInput

    property variant key
    property alias value: textfield.text

    signal changed

    width: 80
    height: 16

    Row {
        anchors { right: parent.right }
        anchors { leftMargin: 2; rightMargin: 2 }
        Text {
            color: "#eeeeee"
            font.pixelSize: 10
            text: key + ": "
        }
        Rectangle {
            height: 16
            width: 25
            color: "#444444"
            TextInput {
                id: textfield
                anchors.fill: parent
                font.pixelSize: 10
                anchors { leftMargin: 2; rightMargin: 2 }
                color: "#eeeeee"
                //text: ""
                selectByMouse: true
            }
        }
    }

    //states: State {
    //    name: "pressed"; when: mouseArea.pressed == true
    //    PropertyChanges { target: shade; opacity: .4 }
    //}
}
