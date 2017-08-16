import QtQuick 2.0
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtGraphicalEffects 1.0

Button {
    id: btn

    style: ButtonStyle {
        background: Rectangle {
            id : btnRect
            border.width: control.activeFocus ? 2 : 1
            border.color: control.pressed || control.checked ? "#353535" : "#252525"
            radius: 4
            gradient: Gradient {
                GradientStop {
                    position: 0
                    color: control.pressed || control.checked ? "#151515" : "#454343"
                }
                GradientStop {
                    position: 1
                    color: control.pressed || control.checked ? "#353535" : "#252525"
                }
            }
        }
    }


}
